<template>
  <div class="d-flex">
    <!-- grade text input container - custom bootstrap -->
    <div class="dropdown w-100 me-3">
      <label :for="`grade-${student.item_id}`" class="form-label"
        >Enter grade
      </label>
      <input
        :id="`grade-${student.item_id}`"
        class="form-control form-control-sm rounded-2 dropdown-toggle"
        :class="gradeError || gradeEmpty ? 'is-invalid' : ''"
        type="text"
        autocomplete="off"
        :value="grade"
        :aria-controls="`grade-${student.item_id}-menu`"
        data-bs-toggle="dropdown"
        required
        @change="gradeChanged($event.target.value)"
        @keydown.tab.exact="false"
        @keydown.down.exact="openMenu"
      />

      <!-- grade input validation errors -->
      <div v-if="gradeError" role="alert" class="invalid-feedback">
        {{ gradeError }}
      </div>

      <div v-else>
        <div v-if="incomplete" class="form-text">
          Student will receive default grade
        </div>
        <div v-if="importSource" class="imported-grade small">
          {{ importSource }} grade: {{ importGrade }}
          <span
            v-if="overrideGrade"
            class="override-icon"
            title="Override grade imported from Canvas Gradebook"
          >
            <i class="fas fa-circle fa-stack-2x" aria-hidden="true"></i>
          </span>
        </div>
        <div v-if="hasChangedGrade" class="small">
          {{ priorGradeText(student) }}
        </div>
      </div>

      <!-- grade input dropdown -->
      <ul
        :id="`grade-${student.item_id}-menu`"
        role="menu"
        :aria-labelledby="`grade-${student.item_id}`"
        class="dropdown-menu m-0 small overflow-y-auto"
        style="max-height: 400px"
        :class="[menuOpen ? 'show' : '']"
        @keydown.esc="closeMenu"
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
            @click.prevent="gradeChanged(opt)"
            v-text="opt"
          ></button>
        </li>
      </ul>
    </div>

    <div>
      <div>
        <!-- incomplete checkbox button -->
        <div class="btn-group btn-group-sm">
          <input
            :id="`incomplete-${student.item_id}`"
            type="checkbox"
            class="me-1"
            autocomplete="off"
            :disabled="!student.allows_incomplete"
            :checked="incomplete"
            @change="incompleteChanged($event.target.checked)"
          />
          <label
            :for="`incomplete-${student.item_id}`"
            :title="inputIncompleteTitle"
            class=""
            >Incomplete</label
          >
        </div>
      </div>

      <div>
        <!-- writing checkbox button -->
        <div v-if="student.is_writing_section" class="btn-group btn-group-sm">
          <input
            :id="`writing-${student.item_id}`"
            type="checkbox"
            class="me-1"
            disabled
            checked
          />
          <label>Writing</label>
        </div>
        <div v-else class="btn-group btn-group-sm">
          <input
            :id="`writing-${student.item_id}`"
            type="checkbox"
            class="me-1"
            :disabled="!student.allows_writing_credit"
            :checked="writing"
            @change="writingChanged($event.target.checked)"
          />
          <label
            :for="`writing-${student.item_id}`"
            :title="inputWritingTitle"
            class=""
            >Writing</label
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useGradeStore } from "@/stores/grade";
import { updateGrade } from "@/utils/data";
import { priorGradeText } from "@/utils/grade";
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
      priorGradeText,
    };
  },
  data() {
    return {
      actualChoices: [],
      grade: "",
      incomplete: false,
      writing: false,
      gradeError: "",
      gradeEmpty: false,
      menuOpen: false,
      saveInProgress: false,
      importSource: null,
      importGrade: null,
      overrideGrade: false,
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
        this.student.date_graded &&
        this.student.grade_status_code === "220" &&
        (this.student.grade !== this.grade ||
          this.student.has_incomplete !== this.incomplete ||
          this.student.has_writing_credit !== this.writing)
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
    closeMenu(e) {
      this.menuOpen = false;
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
      let hasSavedGrade = Object.keys(this.student.saved_grade).length > 0,
        grade = hasSavedGrade
          ? this.student.saved_grade.grade
          : this.student.grade,
        noGradeNow = hasSavedGrade
          ? this.student.saved_grade.no_grade_now
          : this.student.no_grade_now;

      if (this.student.allows_incomplete) {
        this.incomplete = hasSavedGrade
          ? this.student.saved_grade.is_incomplete
          : this.student.has_incomplete;
      }
      if (this.student.allows_writing_credit) {
        this.writing = hasSavedGrade
          ? this.student.saved_grade.is_writing
          : this.student.has_writing_credit;
      }
      if (noGradeNow) {
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

      if (hasSavedGrade) {
        this.importSource = this.student.saved_grade.import_source;
        this.importGrade = this.student.saved_grade.import_grade;
        this.overrideGrade = this.student.saved_grade.is_override_grade;
      }

      this.updateGradeChoices();
      this.updateGradeStatus();
    },
    saveGrade: function () {
      if (!this.saveInProgress) {
        // Prevent duplicate PATCH requests
        this.saveInProgress = true;

        this.updateGradeStatus();

        this.updateGrade(
          this.student.grade_url,
          this.gradeStore.gradeData[this.student.student_id]
        )
          .then((data) => {
            this.grade = data.grade;
            this.incomplete = data.is_incomplete;
            this.is_writing = data.is_writing;
            this.gradeStore.addSaved(this.student.student_id);
          })
          .catch((err) => {
            this.gradeError = err.error;
          })
          .finally(() => {
            this.saveInProgress = false;
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
