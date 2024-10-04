<template>
  <BCard class="shadow-sm rounded-3" header-class="p-3" header="Default">
    <template #header>
      <SectionHeader :section="section" :title="gettext('review_import_grades')" />
    </template>

    <ul v-if="gradeImport.students" class="list-unstyled m-0">
      <li
        v-for="(student, index) in gradeImport.students"
        :key="student.item_id"
        class="border-top pt-2 mt-2"
      >
        <Student :student="student" />
      </li>
    </ul>

    <template #footer>
      <div class="d-flex">
        <div class="text-nowrap">
          <BButton variant="outline-primary" @click="editConversion">
            {{ gettext("conversion_back_calc") }}
          </BButton>
          <BButton variant="primary" @click="importGrades" class="ms-2">
            {{ gettext("import_grades_btn") }}
            <span class="visually-hidden">
              {{ gettext("import_grades_btn_sr") }}
            </span>
          </BButton>
        </div>
      </div>
    </template>
  </BCard>
</template>

<script>
import SectionHeader from "@/components/section/header.vue";
import Student from "@/components/student.vue";
import { useWorkflowStateStore } from "@/stores/state";
import { BButton, BCard } from "bootstrap-vue-next";

export default {
  props: {
    section: {
      type: Object,
      required: true,
    },
  },
  components: {
    SectionHeader,
    Student,
    BButton,
    BCard,
  },
  setup() {
    const appState = useWorkflowStateStore();
    return {
      appState,
    };
  },
  data() {
    return {
      errorResponse: null,
    };
  },
  methods: {
    editConversion: function () {
      this.appState.convertImport();
    },
    importGades: function () {
    },
  },
};
</script>
