<template>
  <section class="view">
    <header class="view-header">
      <div>
        <p class="eyebrow">Student</p>
        <h2>学员管理</h2>
      </div>
    </header>

    <div class="split">
      <form class="panel form" @submit.prevent="submit">
        <h3>新增学员</h3>
        <label>姓名<input v-model="form.name" required /></label>
        <label>电话<input v-model="form.phone" required /></label>
        <label>剩余课时<input v-model.number="form.remaining_hours" type="number" min="0" required /></label>
        <button class="primary" type="submit">
          <UserPlus :size="18" />
          保存学员
        </button>
      </form>

      <section class="panel list-panel">
        <h3>学员列表</h3>
        <table>
          <thead>
            <tr>
              <th>姓名</th>
              <th>电话</th>
              <th>剩余课时</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.id">
              <td>{{ student.name }}</td>
              <td>{{ student.phone }}</td>
              <td>{{ student.remaining_hours }}h</td>
              <td>
                <div class="action-btns">
                  <button class="ghost" @click="openRecharge(student)">
                    <Wallet :size="16" />
                    充值
                  </button>
                  <button class="ghost" @click="openHistory(student)">
                    <History :size="16" />
                    记录
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>

    <div v-if="showRecharge" class="overlay" @click.self="closeRecharge">
      <div class="modal">
        <h3>课时充值 — {{ rechargeTarget.name }}</h3>
        <div class="recharge-info">
          <span>当前剩余课时</span>
          <strong>{{ rechargeTarget.remaining_hours }}h</strong>
        </div>
        <form class="form" @submit.prevent="submitRecharge">
          <label>充值课时数<input v-model.number="rechargeForm.hours" type="number" min="1" max="200" required /></label>
          <label>备注（选填）<input v-model="rechargeForm.remark" placeholder="例如：续费20课时" /></label>
          <div class="modal-actions">
            <button class="ghost" type="button" @click="closeRecharge">取消</button>
            <button class="primary" type="submit">
              <Wallet :size="16" />
              确认充值
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showHistory" class="overlay" @click.self="closeHistory">
      <div class="modal modal-lg">
        <h3>充值记录 — {{ historyTarget.name }}</h3>
        <table v-if="rechargeRecords.length">
          <thead>
            <tr>
              <th>充值课时</th>
              <th>充值前</th>
              <th>充值后</th>
              <th>备注</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rechargeRecords" :key="r.id">
              <td>+{{ r.hours }}h</td>
              <td>{{ r.remaining_before }}h</td>
              <td>{{ r.remaining_after }}h</td>
              <td>{{ r.remark || '—' }}</td>
              <td>{{ formatTime(r.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <EmptyState v-else text="暂无充值记录" />
        <div class="modal-actions">
          <button class="ghost" @click="closeHistory">关闭</button>
        </div>
      </div>
    </div>

    <section class="panel list-panel">
      <h3>充值记录</h3>
      <table>
        <thead>
          <tr>
            <th>学员</th>
            <th>充值课时</th>
            <th>充值前</th>
            <th>充值后</th>
            <th>备注</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="allRecords.length === 0">
            <td colspan="6" style="text-align:center;color:#627d98;">暂无充值记录</td>
          </tr>
          <tr v-for="r in allRecords" :key="r.id">
            <td>{{ getStudentName(r.student_id) }}</td>
            <td>+{{ r.hours }}h</td>
            <td>{{ r.remaining_before }}h</td>
            <td>{{ r.remaining_after }}h</td>
            <td>{{ r.remark || '—' }}</td>
            <td>{{ formatTime(r.created_at) }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </section>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { UserPlus, Wallet, History } from 'lucide-vue-next'
import { studentApi } from '../api/modules'
import EmptyState from '../components/EmptyState.vue'

const props = defineProps({
  students: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['changed'])
const form = reactive({
  name: '',
  phone: '',
  remaining_hours: 20,
})

async function submit() {
  await studentApi.create(form)
  form.name = ''
  form.phone = ''
  form.remaining_hours = 20
  emit('changed')
}

const showRecharge = ref(false)
const rechargeTarget = ref({})
const rechargeForm = reactive({ hours: 10, remark: '' })

function openRecharge(student) {
  rechargeTarget.value = { ...student }
  rechargeForm.hours = 10
  rechargeForm.remark = ''
  showRecharge.value = true
}

function closeRecharge() {
  showRecharge.value = false
}

async function submitRecharge() {
  await studentApi.recharge(rechargeTarget.value.id, {
    hours: rechargeForm.hours,
    remark: rechargeForm.remark || null,
  })
  showRecharge.value = false
  emit('changed')
  loadAllRecords()
}

const showHistory = ref(false)
const historyTarget = ref({})
const rechargeRecords = ref([])

async function openHistory(student) {
  historyTarget.value = { ...student }
  rechargeRecords.value = await studentApi.getRecharges(student.id)
  showHistory.value = true
}

function closeHistory() {
  showHistory.value = false
}

const allRecords = ref([])

async function loadAllRecords() {
  const results = await Promise.all(
    props.students.map((s) => studentApi.getRecharges(s.id))
  )
  allRecords.value = results.flat().sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  )
}

function getStudentName(studentId) {
  const s = props.students.find((s) => s.id === studentId)
  return s ? s.name : '—'
}

function formatTime(dt) {
  const d = new Date(dt)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

watch(() => props.students, loadAllRecords, { immediate: true })
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: #fff;
  border-radius: 10px;
  padding: 24px;
  width: 420px;
  max-width: 92vw;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-lg {
  width: 640px;
}

.modal h3 {
  margin: 0 0 16px;
  font-size: 18px;
}

.recharge-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f0f4f8;
  border-radius: 6px;
  padding: 12px 16px;
  margin-bottom: 14px;
  color: #334e68;
}

.recharge-info strong {
  color: #0f766e;
  font-size: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}

.action-btns {
  display: flex;
  gap: 6px;
}
</style>
