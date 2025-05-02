<template>
  <div class="d-flex mt-2">
    <div
      class="d-flex p-1 rounded-3 me-0"
      :class="[incomplete ? 'bg-primary-subtle' : '']"
    >
      <!-- incomplete checkbox button -->
      <div class="btn-group btn-group-sm me-1">
        <input
          :id="`incomplete-${student.item_id}`"
          type="checkbox"
          class="btn-check"
          autocomplete="off"
          :disabled="!student.allows_incomplete"
          :checked="incomplete"
          @change="incompleteChanged($event.target.checked)"
        />
        <label
          :for="`incomplete-${student.item_id}`"
          :title="inputIncompleteTitle"
          class="btn btn-outline-primary fw-bold rounded-2"
          style="width: 32px"
          ><abbr title="Incomplete" class="text-decoration-none pe-none"
            >I</abbr
          ></label
        >
      </div>

      <!-- grade text input - custom bootstrap -->
      <div class="dropdown ms-1">
        <label :for="`grade-${student.item_id}`" class="visually-hidden"
          >Enter grade
        </label>
        <input
          :id="`grade-${student.item_id}`"
          class="form-control form-control-sm rounded-2 dropdown-toggle border-secondary"
          type="text"
          autocomplete="off"
          :value="grade"
          :placeholder="gradePlaceholder"
          :aria-controls="`grade-${student.item_id}-menu`"
          data-bs-toggle="dropdown"
          @change="gradeChanged($event.target.value)"
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
          <li
            v-for="(opt, index) in actualChoices"
            :key="index"
            role="presentation"
          >
            <button
              role="menuitem"
              class="dropdown-item small"
              type="button"
              :value="opt"
              @click="gradeChanged(opt)"
              v-text="opt"
            ></button>
          </li>
        </ul>
      </div>
    </div>

    <!-- writing checkbox button -->
    <div
      v-if="!student.is_writing_section"
      class="btn-group btn-group-sm p-1 bg-transparent rounded-3"
    >
      <input
        :id="`writing-${student.item_id}`"
        type="checkbox"
        class="btn-check"
        :disabled="!student.allows_writing_credit"
        :checked="writing"
        @change="writingChanged($event.target.checked)"
      />
      <label
        :for="`writing-${student.item_id}`"
        :title="inputWritingTitle"
        class="btn btn-outline-primary fw-bold rounded-2"
        style="width: 32px"
        ><abbr title="Writing" class="text-decoration-none pe-none"
          >W</abbr
        ></label
      >
    </div>
    <div
      v-if="student.is_writing_section"
      class="btn-group btn-group-sm p-1 bg-transparent rounded-3"
      aria-hidden="true"
    >
      <button
        class="btn btn-secondary disabled fw-bold rounded-2"
        style="width: 32px"
      >
        <abbr title="Writing" class="text-decoration-none pe-none">W</abbr>
      </button>
    </div>
  </div>

  <div v-if="incomplete" class="text-start small mb-3 text-muted">
    Student will receive default grade
  </div>

  <div>
    <span v-if="import_source" class="imported-grade small text-muted">
      {{ import_source }} grade: {{ import_grade }}
      <span
        v-if="is_override_grade"
        class="override-icon"
        title="Override grade imported from Canvas Gradebook"
      >
        <i class="fas fa-circle fa-stack-2x" aria-hidden="true"></i>
      </span>
    </span>
    <span role="alert" class="text-danger invalid-grade small">
      {{ gradeError }}
    </span>
  </div>
  <div v-if="hasChangedGrade" class="small text-muted">
    TODO: {{ student.grade_status }}
  </div>
</template>

<script>
import { useGradeStore } from "@/stores/grade";
import { updateGrade } from "@/utils/data";
import {
  incompleteBlocklist,
  normalizeGrade,
  normalizeDefaultGrade,
} from "@/utils/grade";

export default {
  name: "GradeEdit",
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
    const gradeStore = useGradeStore();
    return {
      gradeStore,
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
      inprogress_save: false,
      import_source: null,
      import_grade: null,
      is_override_grade: false,
    };
  },
  computed: {
    gradePlaceholder() {
      return this.incomplete ? "Enter default grade..." : "Enter grade...";
    },
    inputIncompleteTitle() {
      return interpolate(
        this.student.allows_incomplete
          ? this.incomplete
            ? "Click to remove Incomplete for %(student_firstname)s %(student_lastname)s"
            : "Click to assign Incomplete for %(student_firstname)s %(student_lastname)s"
          : "Incomplete not allowed for %(student_firstname)s %(student_lastname)s",
        this.student,
        true
      );
    },
    inputWritingTitle() {
      return interpolate(
        this.student.allows_writing_credit
          ? this.writing
            ? "Click to remove Writing Credit for %(student_firstname)s %(student_lastname)s"
            : "Click to assign Writing Credit for %(student_firstname)s %(student_lastname)s"
          : "Writing Credit not allowed for %(student_firstname)s %(student_lastname)s",
        this.student,
        true
      );
    },
    hasChangedGrade() {
      return (
        this.student.date_graded && this.student.grade_status_code === "220"
      );
    },
  },
  created() {
    this.initializeGrade();
  },
  methods: {
    openMenu(e) {
      this.menuOpen = true;
    },
    updateGradeChoices: function () {
      var valid = [];
      this.gradeChoices.forEach((gc, idx) => {
        let grade = idx === 0 && gc === "" ? gettext("x_no_grade_now") : gc;
        if (this.incomplete && incompleteBlocklist.includes(grade)) {
          return;
        }
        valid.push(grade);
      });
      this.actualChoices = valid;
    },
    incompleteChanged: function (checked) {
      this.incomplete = checked;
      this.updateGradeChoices();
      if (checked) {
        this.grade = normalizeDefaultGrade(this.grade, this.actualChoices);
      }
      this.saveGrade();
    },
    writingChanged: function (checked) {
      this.writing = checked;
      this.saveGrade();
    },
    gradeChanged: function (value) {
      this.grade = normalizeGrade(value);
      this.saveGrade();
      this.menuOpen = false;
    },
    initializeGrade: function () {
      let has_saved_grade = Object.keys(this.student.saved_grade).length > 0,
        grade = has_saved_grade
          ? this.student.saved_grade.grade
          : this.student.grade,
        no_grade_now = has_saved_grade
          ? this.student.saved_grade.no_grade_now
          : this.student.no_grade_now;

      if (this.student.allows_incomplete) {
        this.incomplete = has_saved_grade
          ? this.student.saved_grade.is_incomplete
          : this.student.has_incomplete;
      }
      if (this.student.allows_writing_credit) {
        this.writing = has_saved_grade
          ? this.student.saved_grade.is_writing
          : this.student.has_writing_credit;
      }
      if (no_grade_now) {
        this.grade = gettext("x_no_grade_now");
      } else if (
        grade === null &&
        !this.incomplete &&
        this.gradeChoices.includes("N")
      ) {
        this.grade = "N";
      } else if (grade !== null) {
        this.grade = grade;
      }

      if (has_saved_grade) {
        this.import_source = this.student.saved_grade.import_source;
        this.import_grade = this.student.saved_grade.import_grade;
        this.is_override_grade = this.student.saved_grade.is_override_grade;
      }

      this.updateGradeChoices();
      this.updateGradeStatus();
    },
    saveGrade: function () {
      this.updateGradeStatus();

      // Prevent duplicate PATCH requests
      if (!this.inprogress_save) {
        this.inprogress_save = true;

        this.updateGrade(
          this.student.grade_url,
          this.gradeStore.gradeData[this.student.student_id]
        )
          .then((data) => {
            this.grade = data.grade;
            this.incomplete = data.is_incomplete;
            this.is_writing = data.is_writing;
            this.updateGradeStatus();
          })
          .catch((err) => {
            this.gradeError = err.error;
          })
          .finally(() => {
            this.inprogress_save = false;
          });
      }
    },
    updateGradeStatus: function () {
      this.gradeError = this.gradeStore.validate(
        this.student.student_id,
        this.grade,
        this.incomplete,
        this.writing,
        this.actualChoices
      );
    },
  },
};
</script>
