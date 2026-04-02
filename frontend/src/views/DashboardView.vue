<script setup lang="ts">
import { computed } from "vue";
import { authState } from "@/stores/auth-state";
import AppCard from "@/components/AppCard.vue";

const email = computed(() => authState.user?.email ?? "");

type Tone = "good" | "bad" | "neutral";
type Kpi = { title: string; value: string; sub: string; tone?: Tone };

const kpis: Kpi[] = [
  { title: "累積報酬率", value: "+24.82%", sub: "+3.1%", tone: "good" },
  { title: "勝率", value: "68.4%", sub: "對比平均 52%", tone: "neutral" },
  { title: "最大回撤", value: "-11.2%", sub: "-0.5%", tone: "bad" },
  { title: "夏普值", value: "2.41", sub: "月增 +0.12", tone: "neutral" },
];

type RunStatus = "Completed" | "Failed" | "Running";
type Run = {
  name: string;
  id: string;
  status: RunStatus;
  period: string;
  roi: string;
};

const runs: Run[] = [
  {
    name: "Trend_Following_BTC_6H",
    id: "BT-88291-A",
    status: "Completed",
    period: "Oct 2023 - Mar 2024",
    roi: "+42.15%",
  },
  {
    name: "Mean_Rev_SPY_15M",
    id: "BT-88285-C",
    status: "Failed",
    period: "Jan 2024 - Feb 2024",
    roi: "---",
  },
  {
    name: "Macro_Hedge_Basket",
    id: "BT-88274-B",
    status: "Running",
    period: "Full Year 2023",
    roi: "Processing...",
  },
  {
    name: "Volatility_Breakout_VIX",
    id: "BT-88266-X",
    status: "Completed",
    period: "Q4 2023",
    roi: "+12.80%",
  },
];

function toneTextClass(tone?: Tone) {
  if (tone === "good") return "tone-good";
  if (tone === "bad") return "tone-bad";
  return "tone-neutral";
}

function statusBadgeVariant(status: RunStatus) {
  if (status === "Completed") return "badge-success";
  if (status === "Failed") return "badge-danger";
  return "badge-primary";
}
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <div class="flex items-start justify-between gap-6 flex-wrap">
      <div class="space-y-1">
        <h1 class="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p class="text-sm text-muted-foreground">股票資訊總覽</p>
      </div>
    </div>
    <div class="grid lg:grid-cols-[1.2fr_1fr] gap-4">
      <!-- Left: hero -->
      <AppCard class="h-full" variant="muted" padding="md">
        <div class="flex flex-col justify-between h-full">
          <div class="space-y-2">
            <p class="text-muted-foreground">
              <template v-if="email">
                {{ email }}<br/>歡迎使用 會員系統
              </template>
              <template v-else>
                歡迎使用 會員系統
              </template>
            </p>
          </div>
          <div class="pt-4">
            <div class="flex items-center justify-between gap-2">
              
              <button class="btn btn-primary" type="button" disabled>
                查看報表
              </button>
            </div>
          </div>
        </div>
      </AppCard>

      <!-- Right: grid -->
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

    <!-- Recent runs -->
    <AppCard title="Recent Backtests" subtitle="最近執行與狀態" padding="md">
      <!-- <template #actions>
        <button class="btn btn-outline" type="button" disabled>查看更多</button>
      </template> -->

      <el-table :data="runs" class="app-table w-full" border>
        <el-table-column prop="name" label="Name" min-width="220" />
        <el-table-column prop="id" label="ID" width="140" />

        <el-table-column label="Status" width="140">
          <template #default="{ row }">
            <span class="badge" :class="statusBadgeVariant(row.status)">
              {{ row.status }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="period" label="Period" min-width="200" />
        <el-table-column prop="roi" label="ROI" width="120" />
      </el-table>
    </AppCard>
  </div>
</template>
