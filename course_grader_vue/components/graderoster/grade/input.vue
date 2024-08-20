<template>
  <div class="d-flex mt-2">
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
        class="btn btn-light border fw-bold rounded-2"
        style="width: 32px"
        ><abbr title="Incomplete" class="text-decoration-none pe-none"
          >I</abbr
        ></label
      >
    </div>

    <!-- grade text input - custom bootstrap -->
    <div class="dropdown mx-1">
      <label :for="`grade-${student.item_id}`" class="visually-hidden"
        >Enter grade</label
      >
      <input
        class="form-control form-control-sm rounded-2 dropdown-toggle"
        type="text"
        autocomplete="off"
        :id="`grade-${student.item_id}`"
        :value="grade"
        :disabled="student.is_submitted"
        :placeholder="gradePlaceholder"
        @change="gradeChanged($event.target.value)"
        :aria-controls="`grade-${student.item_id}-menu`"
        data-bs-toggle="dropdown"
        @keydown.tab.exact="false"
        @keydown.down.exact="openMenu"
      />
      <ul
        :id="`grade-${student.item_id}-menu`"
        role="menu"
        :aria-labelledby="`grade-${student.item_id}`"
        class="dropdown-menu m-0 small overflow-y-auto"
        style="max-height: 400px"
        :class="[menuOpen ? 'show' : '']"
      >
        <li v-for="opt in actualChoices" role="presentation">
          <button
            role="menuitem"
            class="dropdown-item small"
            type="button"
            :value="opt"
            @click="gradeChanged(opt)"
          >
            {{ opt }}
          </button>
        </li>
      </ul>
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
        class="btn btn-light border fw-bold rounded-2"
        style="width: 32px"
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
      {{ gradeError }}
    </span>
  </div>
</template>

<script>
import { updateGrade } from "@/utils/data";
import {
  incompleteBlocklist,
  normalizeGrade,
  validateGrade,
} from "@/utils/grade";

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
      actualChoices: [],
      grade: "",
      incomplete: false,
      writing: false,
      gradeError: "",
      menuOpen: false,
    };
  },
  computed: {
    gradePlaceholder() {
      return this.incomplete ? "Enter default grade..." : "Enter grade...";
    },
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
    openMenu(e) {
      this.menuOpen = true;
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

        if (this.incomplete && incompleteBlocklist.includes(grade)) {
          continue;
        }
        valid.push(grade);
      }
      this.actualChoices = valid;
    },
    incompleteChanged: function (checked) {
      this.incomplete = checked;
      this.updateGradeChoices();
      this.gradeError = validateGrade(
        this.grade,
        this.incomplete,
        this.actualChoices
      );
      this.saveGrade();
    },
    writingChanged: function (checked) {
      this.writing = checked;
      this.saveGrade();
    },
    gradeChanged: function (value) {
      this.grade = normalizeGrade(value);
      this.gradeError = validateGrade(
        this.grade,
        this.incomplete,
        this.actualChoices
      );
      this.saveGrade();
      this.menuOpen = false;
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
      } else if (this.student.grade !== null) {
        this.grade = this.student.grade;
      }
      this.gradeError = validateGrade(
        this.grade,
        this.incomplete,
        this.actualChoices
      );
    },
    saveGrade: function () {},
  },
  created() {
    this.initializeGrade();
  },
};
</script>
