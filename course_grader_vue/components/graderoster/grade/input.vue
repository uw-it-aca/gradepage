<template>
  <div class="d-flex">
    <div class="input-group input-group-sm me-2">
      <!-- incomplete checkbox button -->
      <div class="btn-group btn-group-sm">
        <input
          type="checkbox"
          class="btn-check"
          autocomplete="off"
          :id="`incomplete-${student.item_id}`"
          :disabled="!student.allows_incomplete || student.is_submitted"
          :checked="incomplete"
          @change="incompleteChanged($event.target.checked)"
        />
        <label
          :for="`incomplete-${student.item_id}`"
          :title="inputIncompleteTitle"
          class="btn btn-outline-secondary fw-bold rounded-start-2"
          style="width: 31px"
          ><abbr title="Incomplete" class="text-decoration-none pe-none"
            >I</abbr
          ></label
        >
      </div>

      <div class="dropdown">
        <!-- grade text input - custom bootstrap -->
        <input
          class="form-control form-control-sm rounded-start-0 rounded-end border-secondary"
          type="text"
          aria-label=""
          aria-expanded="true"
          aria-autocomplete="list"
          aria-owns="owned_listbox"
          aria-activedescendant="selected_option"
          aria-required="true"
          :id="`grade-${student.item_id}`"
          :value="grade"
          :disabled="student.is_submitted"
          :placeholder="[
            incomplete ? 'Enter default grade...' : 'Enter grade...',
          ]"
          data-bs-toggle="dropdown"
          @input="gradeChanged($event.target.value)"
        />
        <ul class="dropdown-menu m-0 small overflow-y-auto" style="max-height: 400px;">
          <li v-for="g in choices">
            <button class="dropdown-item small" :value="g" type="button" @click="insertGradeChoice(`grade-${student.item_id}`, g)">{{ g }}</button>
          </li>
        </ul>
      </div>
    </div>

    <!-- writing checkbox button -->
    <div v-if="!student.is_writing_section" class="btn-group btn-group-sm">
      <input
        type="checkbox"
        class="btn-check"
        :id="`writing-${student.item_id}`"
        :disabled="!student.allows_writing_credit || student.is_submitted"
        :checked="writing"
        @change="writingChanged($event.target.checked)"
      />
      <label
        :for="`writing-${student.item_id}`"
        :title="inputWritingTitle"
        class="btn btn-outline-secondary fw-bold rounded-2"
        ><abbr title="Writing" class="text-decoration-none pe-none"
          >W</abbr
        ></label
      >
    </div>
  </div>

  <div v-if="incomplete" class="text-start small mb-3 text-muted">
    Student will receive default grade
  </div>

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
    <span role="alert" class="text-danger invalid-grade small">
      {{ errorText }}
    </span>
  </div>
</template>

<script>
import { updateGrade } from "@/utils/data";
import { normalizeGrade, validateGrade } from "@/utils/grade";

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
      errorText: null,
      blah: null,
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
    insertGradeChoice: function (a, b) {
      // get the correct text input by id
      let input = document.getElementById(a);
      // set the input value to whatever choice was clicked
      let choice = b
      input.value = choice;
    },
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
    incompleteChanged: function (checked) {
      this.incomplete = checked;
      this.updateGradeChoices();
      this.errorText = validateGrade(
        this.grade, this.incomplete, this.choices, this.incompleteBlocklist);
    },
    writingChanged: function (checked) {
      this.writing = checked;
    },
    gradeChanged: function (value) {
      this.grade = normalizeGrade(value);
      this.errorText = validateGrade(
        this.grade, this.incomplete, this.choices, this.incompleteBlocklist);
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
    saveGrade: function () {},
  },
  created() {
    this.initializeGrade();
  },
};
</script>
