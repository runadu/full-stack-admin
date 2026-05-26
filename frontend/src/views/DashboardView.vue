<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { authState } from "@/stores/auth-state";
import AppCard from "@/components/AppCard.vue";
import { listStocksApi, type Stock } from "@/api/stocks";

const email = computed(() => authState.user?.email ?? "");
const loading = ref(false);
const error = ref("");
const items = ref<Stock[]>([]);

type Tone = "good" | "bad" | "neutral";
type Kpi = { title: string; value: string; sub: string; tone?: Tone };

let disposed = false;

onMounted(() => {
  disposed = false;
  load();
});

onBeforeUnmount(() => {
  disposed = true;
});

async function load() {
  loading.value = true;
  error.value = "";

  try {
    const data = await listStocksApi();
    if (disposed) return;
    items.value = data;
  } catch (e: any) {
    if (disposed) return;
    error.value = e?.message || "載入失敗，請稍後再試";
  } finally {
    if (disposed) return;
    loading.value = false;
  }
}

function toneTextClass(tone?: Tone) {
  if (tone === "good") return "tone-good";
  if (tone === "bad") return "tone-bad";
  return "tone-neutral";
}

function formatPrice(value: number, currency = "USD") {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPriceDate(value: string) {
  return new Intl.DateTimeFormat("zh-TW", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(`${value}T00:00:00`));
}

function formatCacheStatus(value?: string | null) {
  if (value === "hit") return "快取命中";
  if (value === "miss") return "即時抓取";
  if (value === "stale") return "錯誤時回退快取";
  return "未提供";
}

function uniqueBySymbol(rows: Stock[]) {
  const seen = new Set<string>();
  return rows.filter((row) => {
    if (seen.has(row.symbol)) return false;
    seen.add(row.symbol);
    return true;
  });
}

const sortedItems = computed(() => [...items.value].sort((a, b) => b.close_price - a.close_price));

const sharedCurrency = computed(() => items.value[0]?.currency ?? "USD");

const latestPriceDate = computed(() => {
  const dates = items.value
    .map((item) => item.price_date)
    .filter(Boolean)
    .sort();
  return dates.length > 0 ? dates[dates.length - 1] : "";
});

const warningText = computed(() => {
  const warnings = Array.from(
    new Set(
      items.value.map((item) => item.warning).filter((value): value is string => Boolean(value)),
    ),
  );
  return warnings.join(" | ");
});

const kpis = computed<Kpi[]>(() => {
  if (items.value.length === 0) {
    return [
      { title: "追蹤股票數", value: "--", sub: "等待 Massive 資料" },
      { title: "平均收盤價", value: "--", sub: "等待 Massive 資料" },
      { title: "最高收盤價", value: "--", sub: "等待 Massive 資料" },
      { title: "最低收盤價", value: "--", sub: "等待 Massive 資料" },
    ];
  }

  const total = items.value.reduce((sum, item) => sum + item.close_price, 0);
  const average = total / items.value.length;
  const highest = sortedItems.value[0];
  const lowest = sortedItems.value[sortedItems.value.length - 1] ?? sortedItems.value[0];
  const latestDateText = latestPriceDate.value
    ? `資料日 ${formatPriceDate(latestPriceDate.value)}`
    : "最近交易日";

  if (!highest || !lowest) {
    return [
      { title: "追蹤股票數", value: "--", sub: "等待 Massive 資料" },
      { title: "平均收盤價", value: "--", sub: "等待 Massive 資料" },
      { title: "最高收盤價", value: "--", sub: "等待 Massive 資料" },
      { title: "最低收盤價", value: "--", sub: "等待 Massive 資料" },
    ];
  }

  return [
    {
      title: "追蹤股票數",
      value: String(items.value.length),
      sub: `${formatCacheStatus(items.value[0]?.cache_status)} / ${latestDateText}`,
      tone: "neutral",
    },
    {
      title: "平均收盤價",
      value: formatPrice(average, sharedCurrency.value),
      sub: `共 ${items.value.length} 檔`,
      tone: "neutral",
    },
    {
      title: "最高收盤價",
      value: formatPrice(highest.close_price, highest.currency),
      sub: `${highest.symbol} / ${highest.name}`,
      tone: "good",
    },
    {
      title: "最低收盤價",
      value: formatPrice(lowest.close_price, lowest.currency),
      sub: `${lowest.symbol} / ${lowest.name}`,
      tone: "bad",
    },
  ];
});

const tableRows = computed(() => uniqueBySymbol(sortedItems.value));
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <div class="flex items-start justify-between gap-6 flex-wrap">
      <div class="space-y-1">
        <h1 class="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p class="text-sm text-muted-foreground">股票資訊總覽</p>
      </div>
      <div>
        <div class="text-sm text-muted-foreground/90">
          <template v-if="loading">正在同步 Massive 資料...</template>
          <template v-else-if="latestPriceDate">
            最近交易日：{{ formatPriceDate(latestPriceDate) }}
          </template>
          <template v-else>目前尚無可顯示資料</template>
        </div>
      </div>
    </div>

    <div
      v-if="error"
      class="rounded-md border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger"
      role="alert"
    >
      {{ error }}
    </div>

    <div
      v-else-if="warningText"
      class="rounded-md border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-warning"
      role="status"
    >
      {{ warningText }}
    </div>

    <div class="grid lg:grid-cols-[1.2fr_1fr] gap-4">
      <AppCard class="h-full" variant="muted" padding="md">
        <div class="flex flex-col justify-between h-full gap-6">
          <div class="space-y-2">
            <p class="text-muted-foreground">
              <template v-if="email"> {{ email }}<br />歡迎使用 會員系統 </template>
              <template v-else> 歡迎使用 會員系統 </template>
            </p>
            <p className="text-sm text-muted-foreground/90 leading-relaxed">
              本頁股票資訊透過
              <a
                href="https://massive.com/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-primary underline-offset-4 hover:underline"
              >
                Massive API
              </a>
              取得，資料可能有所延遲，請以交易平台或官方公告為準。
            </p>
          </div>

          <div class="pt-4">
            <div class="flex items-center justify-between gap-2">
              <RouterLink class="btn btn-primary" :to="{ name: 'stocks' }"> 查看股票 </RouterLink>
            </div>
          </div>
        </div>
      </AppCard>

      <div class="grid grid-cols-2 gap-4">
        <AppCard v-for="k in kpis" :key="k.title" padding="sm" class="h-full">
          <div class="flex flex-col justify-between h-full">
            <p class="text-sm text-muted-foreground">{{ k.title }}</p>

            <div class="space-y-1">
              <p class="text-2xl font-bold" :class="toneTextClass(k.tone)">
                {{ k.value }}
              </p>
              <p class="text-sm" :class="['tone-sub', toneTextClass(k.tone)]">
                {{ k.sub }}
              </p>
            </div>
          </div>
        </AppCard>
      </div>
    </div>

    <AppCard title="Massive Snapshot" subtitle="依收盤價排序的最新股票資料" padding="md">
      <template #actions>
        <button class="btn btn-outline" type="button" :disabled="loading" @click="load">
          重新整理
        </button>
      </template>

      <div v-if="!loading && !error && tableRows.length === 0" class="py-10">
        <el-empty description="目前沒有股票資料" />
      </div>

      <el-table v-else :data="tableRows" v-loading="loading" class="app-table w-full" border>
        <el-table-column prop="symbol" label="Symbol" width="140" />
        <el-table-column prop="name" label="Name" min-width="240" />
        <el-table-column prop="close_price" label="Close" width="160">
          <template #default="{ row }">
            <span class="font-medium">
              {{ formatPrice(row.close_price, row.currency) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="price_date" label="Date" width="140">
          <template #default="{ row }">
            {{ formatPriceDate(row.price_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="cache_status" label="Cache" width="160">
          <template #default="{ row }">
            {{ formatCacheStatus(row.cache_status) }}
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="120" />
      </el-table>
    </AppCard>
  </div>
</template>
