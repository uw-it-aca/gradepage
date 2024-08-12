<template>
  <div class="input-group">

    <!-- incomplete checkbox button -->
    <div
      class="btn-group d-inline-block"
      role="group"
      aria-label="Basic checkbox toggle button group"
    >
      <input
        type="checkbox"
        class="btn-check"
        autocomplete="off"
        :id="`incomplete-${student.item_id}`"
          :disabled="!student.allows_incomplete || student.is_submitted"
          :checked="incomplete"
          @change="incompleteChanged($event)"
      />
      <label  :for="`incomplete-${student.item_id}`"
      :title="inputIncompleteTitle" class="btn btn-outline-secondary" for="btncheck1" style="width:38px;">I</label>
    </div>

    <!-- grade text input -->
    <input
      class="form-control rounded-end border-secondary"
      type="text"
      aria-label=""
      aria-expanded="true"
      aria-autocomplete="list"
      aria-owns="owned_listbox"
      aria-activedescendant="selected_option"
      aria-required="true"
      :id="`grade-${student.item_id}`"
      :list="`datalistOptions-${student.item_id}`"
      :value="grade"
      :disabled="student.is_submitted"
      :placeholder="[incomplete ? 'Enter default grade...' : 'Enter grade...']"
    />
    <datalist :id="`datalistOptions-${student.item_id}`">
      <option v-for="g in choices" :value="g"></option>
    </datalist>


    <!-- writing checkbox button -->
    <div
     v-if="!student.is_writing_section"
      class="btn-group ms-2"
      role="group"
      aria-label="Basic checkbox toggle button group"
    >
      <input
        type="checkbox"
        class="btn-check"
        autocomplete="off"
        value="1"
          :id="`writing-${student.item_id}`"
          :disabled="!student.allows_writing_credit || student.is_submitted"
          :checked="writing"
      />
      <label :for="`writing-${student.item_id}`" :title="inputWritingTitle" class="btn btn-outline-secondary">W</label>
    </div>

  </div>
  <div v-if="incomplete" class="text-start small mb-3">
    Student will receive default grade</div>

  <div :id="`status-${student.item_id}`">
    <span v-if="student.import_source" class="imported-grade">
      {{ student.import_source }} grade: {{ student.import_grade }}
      <span
        v-if="is_override_grade"
        class="override-icon"
        title="Override grade imported from Canvas Gradebook"
      >
        <i
          class="fas fa-circle fa-stack-2x"
          title="Override grade imported from Canvas Gradebook"
          aria-hidden="true"
        >
        </i>
      </span>
    </span>
    <span role="alert" class="text-danger invalid-grade">
      Invalid grade text here
    </span>
  </div>
</template>

<script>
import { updateGrade } from "@/utils/data";

export default {
  props: {
    student: {
      type: Object,
      required: true,
    },
    gradeChoices: {
      type: Array,
      required: true,
    },
  },
  setup() {
    return {
      updateGrade,
    };
  },
  data() {
    return {
      incompleteBlocklist: [gettext("x_no_grade_now"), "N", "CR"],
      choices: [],
      grade: null,
      incomplete: false,
      writing: false,
    };
  },
  computed: {
    inputIncompleteTitle() {
      return this.student.allows_incomplete
        ? ""
        : "Incomplete not allowed for " +
            this.student.student_firstname +
            " " +
            this.student.student_lastname;
    },
    inputWritingTitle() {
      return this.student.allows_writing_credit
        ? ""
        : "Writing Credit not allowed for " +
            this.student.student_firstname +
            " " +
            this.student.student_lastname;
    },
  },
  methods: {
    updateGradeChoices: function () {
      var i,
        len,
        grade,
        valid = [];
      for (i = 0, len = this.gradeChoices.length; i < len; i++) {
        grade =
          i === 0 && this.gradeChoices[i] === ""
            ? gettext("x_no_grade_now")
            : this.gradeChoices[i];

        if (this.incomplete && this.incompleteBlocklist.includes(grade)) {
          continue;
        }
        valid.push(grade);
      }
      this.choices = valid;
    },
    incompleteChanged: function (e) {
      this.$nextTick(() => {
        this.incomplete = e.target.checked;
        this.updateGradeChoices();
      });
    },
    initializeGrade: function () {
      this.updateGradeChoices();
      if (this.student.allows_incomplete) {
        this.incomplete = this.student.has_incomplete;
      }
      if (this.student.allows_writing_credit) {
        this.writing = this.student.has_writing_credit;
      }
      if (this.student.no_grade_now) {
        this.grade = gettext("x_no_grade_now");
      } else if (
        this.student.grade === null &&
        !this.student.has_incomplete &&
        this.gradeChoices.includes("N")
      ) {
        this.grade = "N";
      } else {
        this.grade = this.student.grade;
      }
    },
    normalizeGrade: function (grade) {
      grade = grade.trim();
      if (grade.match(/^(?:n|nc|p|h|hw|f|hp|i|cr)$/i)) {
        grade = grade.toUpperCase();
      } else if (grade.match(/^x/i)) {
        grade = gettext("x_no_grade_now");
      } else {
        grade = grade.replace(/^([0-4])?\.([0-9])0+$/, "$1.$2");
        grade = grade.replace(/^\.([0-9])$/, "0.$1");
        grade = grade.replace(/^([0-4])\.?$/, "$1.0");
      }
      return grade;
    },
    validateGrade: function () {
      var is_incomplete,
        is_valid,
        is_hypenated,
        is_cnc,
        is_hhppf,
        is_undergrad_numeric,
        is_grad_numeric,
        text;
    },
    saveGrade: function () {},
  },
  created() {
    this.initializeGrade();
  },
};
</script>
