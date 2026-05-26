<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import AppDialog from "@/components/AppDialog.vue";
import { listStocksApi, type Stock } from "@/api/stocks";
import { ScanEye } from "lucide-vue-next";

const loading = ref(false);
const error = ref("");
const items = ref<Stock[]>([]);

// pagination
const page = ref(1);
const pageSize = ref(10);
const total = computed(() => items.value.length);

const tableData = computed(() => {
  const start = (page.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return items.value.slice(start, end);
});

const rangeText = computed(() => {
  if (total.value === 0) return { from: 0, to: 0, total: 0 };
  const from = (page.value - 1) * pageSize.value + 1;
  const to = Math.min(page.value * pageSize.value, total.value);
  return { from, to, total: total.value };
});

function onPageChange(p: number) {
  page.value = p;
}

function onSizeChange(size: number) {
  pageSize.value = size;
  page.value = 1;
}

// lifecycle-safe flag
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
    page.value = 1;
  } catch (e: any) {
    if (disposed) return;
    error.value = e?.message || "載入失敗，請稍後再試";
  } finally {
    if (disposed) return;
    loading.value = false;
  }
}

// Detail dialog
const detailOpen = ref(false);
const selected = ref<Stock | null>(null);

function openDetail(row: Stock) {
  selected.value = row;
  detailOpen.value = true;
}

function formatPrice(value: number, currency: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatSignedPrice(value: number, currency: string) {
  const formatted = formatPrice(Math.abs(value), currency);
  if (value > 0) return `+${formatted}`;
  if (value < 0) return `-${formatted}`;
  return formatted;
}

function formatPercent(value: number) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function formatVolume(value: number) {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(value);
}

function formatRange(row: Stock) {
  return `${formatPrice(row.low_price, row.currency)} - ${formatPrice(row.high_price, row.currency)}`;
}

function formatPriceDate(value: string) {
  return new Intl.DateTimeFormat("zh-TW", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(`${value}T00:00:00`));
}

function formatDataDelay(value: string) {
  if (value === "end_of_day") return "收盤資料";
  return value;
}

function toneTextClass(value: number) {
  if (value > 0) return "tone-good";
  if (value < 0) return "tone-bad";
  return "tone-neutral";
}
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-6">
    <div class="flex items-start justify-between gap-6 flex-wrap">
      <div class="space-y-1">
        <h1 class="text-3xl font-bold tracking-tight">Stocks</h1>
        <p class="text-sm text-muted-foreground">股票清單與基本資訊</p>
      </div>
    </div>
    <div
      v-if="error"
      class="rounded-md border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger"
      role="alert"
    >
      {{ error }}
    </div>

    <div>
      <div v-if="!loading && !error && total === 0" class="py-10">
        <el-empty description="目前沒有股票資料">
          <button class="btn btn-primary" type="button" @click="load">重新載入</button>
        </el-empty>
      </div>
      <div
        v-if="!loading && !error && total > 0"
        class="mb-4 rounded-xl border border-border/60 bg-surface/70 px-4 py-3 text-sm text-muted-foreground"
      >
        目前顯示的是最近可用交易日的日線資料，包含 OHLC、成交量、VWAP 與日內漲跌，不是盤中即時報價。
      </div>
      <el-table
        v-if="loading || error || total > 0"
        :data="tableData"
        v-loading="loading"
        class="app-table w-full"
        border
      >
        <el-table-column label="Stock" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="min-w-0 space-y-1">
              <div class="flex items-center gap-2 min-w-0">
                <span class="font-semibold text-foreground shrink-0">{{ row.symbol }}</span>
                <span class="text-sm text-muted-foreground truncate">{{ row.name }}</span>
              </div>
              <div class="text-xs text-muted-foreground">
                {{ formatPriceDate(row.price_date) }} / {{ formatDataDelay(row.data_delay) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="close_price" label="Close" width="132">
          <template #default="{ row }">
            <span class="font-medium">
              {{ formatPrice(row.close_price, row.currency) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Change" width="132">
          <template #default="{ row }">
            <div class="space-y-1">
              <div class="font-medium" :class="toneTextClass(row.day_change)">
                {{ formatSignedPrice(row.day_change, row.currency) }}
              </div>
              <div class="text-xs" :class="toneTextClass(row.day_change)">
                {{ formatPercent(row.day_change_percent) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="H/L" width="144">
          <template #default="{ row }">
            <div class="space-y-1 text-sm">
              <div>{{ formatPrice(row.high_price, row.currency) }}</div>
              <div class="text-muted-foreground">
                {{ formatPrice(row.low_price, row.currency) }}
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="Vol" width="120" align="right">
          <template #default="{ row }">
            <span>{{ formatVolume(row.volume) }}</span>
          </template>
        </el-table-column>

        <el-table-column label="" width="88" align="right">
          <template #default="{ row }">
            <div class="flex justify-end gap-2">
              <button class="btn btn-outline btn-sm" type="button" @click="openDetail(row)">
                <ScanEye class="h-4 w-4" />
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > 0" class="mt-4 flex items-center justify-between gap-3 flex-wrap">
        <p class="text-sm text-muted-foreground">
          第
          <span class="text-foreground font-medium">{{ rangeText.from }}</span>
          -
          <span class="text-foreground font-medium">{{ rangeText.to }}</span>
          項，共
          <span class="text-foreground font-medium">{{ total }}</span>
          項
        </p>

        <el-pagination
          class="app-pagination"
          background
          layout="sizes, prev, pager, next"
          :total="total"
          :current-page="page"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          @update:current-page="onPageChange"
          @size-change="onSizeChange"
        >
        </el-pagination>
      </div>
    </div>
  </div>

  <AppDialog
    v-model="detailOpen"
    :title="selected?.name || selected?.symbol || 'Stock Detail'"
    width="min(92vw, 720px)"
    :showFooter="false"
    cancelText="Close"
    @cancel="detailOpen = false"
  >
    <div class="grid gap-3 sm:grid-cols-2">
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3 min-w-0">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Name</div>
        <div class="mt-1 font-medium text-foreground break-words">{{ selected?.name }}</div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Symbol</div>
        <div class="mt-1 font-medium text-foreground">{{ selected?.symbol }}</div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Close</div>
        <div class="mt-1 text-lg font-semibold text-foreground">
          {{ selected ? formatPrice(selected.close_price, selected.currency) : "" }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Day Change</div>
        <div
          class="mt-1 font-medium"
          :class="selected ? toneTextClass(selected.day_change) : 'text-foreground'"
        >
          {{
            selected
              ? `${formatSignedPrice(selected.day_change, selected.currency)} (${formatPercent(selected.day_change_percent)})`
              : ""
          }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Open</div>
        <div class="mt-1 font-medium text-foreground">
          {{ selected ? formatPrice(selected.open_price, selected.currency) : "" }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">High / Low</div>
        <div class="mt-1 font-medium text-foreground break-words">
          {{
            selected
              ? `${formatPrice(selected.high_price, selected.currency)} / ${formatPrice(selected.low_price, selected.currency)}`
              : ""
          }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Volume</div>
        <div class="mt-1 font-medium text-foreground">
          {{ selected ? formatVolume(selected.volume) : "" }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">VWAP</div>
        <div class="mt-1 font-medium text-foreground">
          {{
            selected && selected.vwap_price != null
              ? formatPrice(selected.vwap_price, selected.currency)
              : "N/A"
          }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Trades</div>
        <div class="mt-1 font-medium text-foreground">
          {{ selected?.trade_count != null ? formatVolume(selected.trade_count) : "N/A" }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Date</div>
        <div class="mt-1 font-medium text-foreground">
          {{ selected ? formatPriceDate(selected.price_date) : "" }}
        </div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Currency</div>
        <div class="mt-1 font-medium text-foreground">{{ selected?.currency }}</div>
      </div>
      <div class="rounded-lg border border-border/70 bg-surface/70 p-3">
        <div class="text-xs uppercase tracking-wide text-muted-foreground">Source / Delay</div>
        <div class="mt-1 font-medium text-foreground break-words">
          {{ selected?.source?.toUpperCase() }} /
          {{ selected ? formatDataDelay(selected.data_delay) : "" }}
        </div>
      </div>
    </div>
  </AppDialog>
</template>
