<script setup lang="ts">
import { reactive, ref, watch, computed } from "vue";
import type { FormInstance, FormRules } from "element-plus";
import { useRouter } from "vue-router";
import { registerApi } from "@/api/accounts";
import AuthSidePanel from "@/views/auth/components/AuthSidePanel.vue";
import Header from "@/layouts/Header.vue";
import { useTheme } from "@/stores/theme";
import type { ApiError } from "@/api/http";

const { isDark, toggleTheme } = useTheme();
const router = useRouter();

const loading = ref(false);
const error = ref("");
const success = ref("");

const formRef = ref<FormInstance>();

const form = reactive({
  email: "",
  password: "",
  confirmPassword: "",
  terms: false,
});

const strength = computed(() => {
  const p = form.password;
  if (!p) return { label: "密碼強度：—", level: 0 };

  let score = 0;
  if (p.length >= 8) score++;
  if (p.length >= 12) score++;
  if (/[a-z]/.test(p)) score++;
  if (/[A-Z]/.test(p)) score++;
  if (/[0-9]/.test(p)) score++;
  if (/[^A-Za-z0-9]/.test(p)) score++;

  let level = 0;
  if (score <= 2) level = 1;
  else if (score === 3) level = 2;
  else if (score === 4) level = 3;
  else level = 4;

  const labelMap = [
    "密碼強度：—",
    "密碼強度：弱",
    "密碼強度：普通",
    "密碼強度：良好",
    "密碼強度：強",
  ];

  return { label: labelMap[level], level };
});

const rules: FormRules<typeof form> = {
  email: [
    { required: true, message: "請輸入 Email", trigger: "blur" },
    { type: "email", message: "Email 格式不正確", trigger: ["blur", "change"] },
  ],
  password: [
    { required: true, message: "請輸入密碼", trigger: "blur" },
    { min: 6, message: "密碼至少 6 碼", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "請再次輸入密碼", trigger: "blur" },
    {
      validator: (_rule, value, callback) => {
        if (!value) return callback();
        if (value !== form.password)
          return callback(new Error("兩次密碼不一致"));
        callback();
      },
      trigger: ["blur", "change"],
    },
  ],
  terms: [
    {
      validator: (_rule, value, callback) => {
        if (value) return callback();
        callback(new Error("請先勾選「我已閱讀並同意服務條款」"));
      },
      trigger: "change",
    },
  ],
};

watch(
  () => [form.email, form.password, form.confirmPassword, form.terms],
  () => {
    if (error.value) error.value = "";
    if (success.value) success.value = "";
  },
);

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function onSubmit() {
  error.value = "";
  success.value = "";

  const ok = await formRef.value?.validate().catch(() => false);
  if (!ok) return;

  loading.value = true;
  try {
    await registerApi({
      email: form.email.trim(),
      password: form.password,
    });

    success.value = "註冊成功，請重新登入";

    await sleep(600);
    await router.replace({ name: "login" });
  } catch (e: unknown) {
    const err = e as ApiError | any;
    const status = Number(err?.status ?? 0);

    if (status === 409) {
      error.value = "這個 Email 已經註冊過了";
      return;
    }

    if (status === 422) {
      error.value = err?.message || "資料格式不正確，請檢查 Email / 密碼";
      return;
    }

    error.value = err?.message || "註冊失敗，請稍後再試";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <Header variant="auth" :isDark="isDark" :toggleTheme="toggleTheme" />

  <div
    class="min-h-[calc(100vh-64px)] flex flex-col lg:flex-row overflow-hidden"
  >
    <AuthSidePanel />

    <section
      class="relative flex lg:w-1/2 flex-col justify-center items-center px-6 bg-surface overflow-y-auto"
    >
      <div class="w-full max-w-[480px] space-y-8 my-auto">
        <div class="space-y-2">
          <h2 class="text-3xl font-bold tracking-tight text-foreground">
            建立帳號
          </h2>
          <p class="text-muted-foreground">加入會員系統</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
          class="mt-8 space-y-6"
          @submit.prevent="onSubmit"
        >
          <el-form-item label="Email" prop="email">
            <el-input
              v-model="form.email"
              type="email"
              size="large"
              autocomplete="email"
            />
          </el-form-item>

          <el-form-item label="密碼" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              size="large"
              autocomplete="new-password"
            />
          </el-form-item>

          <div class="-mt-2">
            <div class="mt-2 flex gap-1 h-1">
              <div
                class="flex-1 rounded-full"
                :class="strength.level >= 1 ? 'bg-primary' : 'bg-muted'"
              />
              <div
                class="flex-1 rounded-full"
                :class="strength.level >= 2 ? 'bg-primary' : 'bg-muted'"
              />
              <div
                class="flex-1 rounded-full"
                :class="strength.level >= 3 ? 'bg-primary' : 'bg-muted'"
              />
              <div
                class="flex-1 rounded-full"
                :class="strength.level >= 4 ? 'bg-primary' : 'bg-muted'"
              />
            </div>
            <p class="text-xs text-muted-foreground mt-2">
              {{ strength.label }}
            </p>
          </div>

          <el-form-item label="確認密碼" prop="confirmPassword">
            <el-input
              v-model="form.confirmPassword"
              type="password"
              show-password
              size="large"
              autocomplete="new-password"
            />
          </el-form-item>

          <el-form-item prop="terms">
            <el-checkbox v-model="form.terms">
              <span class="text-sm text-muted-foreground"
                >我已閱讀並同意服務條款</span
              >
            </el-checkbox>
          </el-form-item>

          <div
            v-if="error"
            class="rounded-lg border border-danger bg-danger/10 px-3 py-2 text-sm text-danger"
          >
            {{ error }}
          </div>

          <div
            v-if="success"
            class="rounded-lg border border-success bg-success/10 px-3 py-2 text-sm text-success"
          >
            {{ success }}
          </div>

          <button type="submit" :disabled="loading" class="btn-primary w-full">
            {{ loading ? "建立中..." : "建立帳號" }}
          </button>
        </el-form>

        <div class="pt-4 text-center text-sm text-muted-foreground">
          已經有帳號？
          <button
            type="button"
            class="font-semibold text-foreground underline underline-offset-4 hover:opacity-70"
            @click="router.push('/login')"
          >
            前往登入
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
