<template>
  <div class="input-group mb-3">
    <div class="input-group-text">
      <input
        id="inputIncomplete"
        class="form-check-input mt-0 me-1"
        type="checkbox"
        value=""
        aria-label="Checkbox for following text input"
      />
      <label>Incomplete</label>
    </div>

    <input
      type="text"
      class="form-control"
      list="datalistOptions"
      id="exampleDataList"
      placeholder=""
    />
    <datalist id="datalistOptions">
      <option value="X (No grade now)"></option>
      <option value="4.0"></option>
      <option value="3.9"></option>
      <option value="3.8"></option>
      <option value="3.7"></option>
      <option value="3.6"></option>
      <option value="3.5"></option>
      <option value="3.4"></option>
      <option value="3.3"></option>
      <option value="3.2"></option>
      <option value="3.1"></option>
      <option value="3.0"></option>
      <option value="2.9"></option>
      <option value="2.8"></option>
      <option value="2.7"></option>
      <option value="2.6"></option>
      <option value="2.5"></option>
      <option value="2.4"></option>
      <option value="2.3"></option>
      <option value="2.2"></option>
      <option value="2.1"></option>
      <option value="2.0"></option>
      <option value="1.9"></option>
      <option value="1.8"></option>
      <option value="1.7"></option>
      <option value="1.6"></option>
      <option value="1.5"></option>
      <option value="1.4"></option>
      <option value="1.3"></option>
      <option value="1.2"></option>
      <option value="1.1"></option>
      <option value="1.0"></option>
      <option value="0.9"></option>
      <option value="0.8"></option>
      <option value="0.7"></option>
      <option value="0.0"></option>
    </datalist>

    <div class="input-group-text">
      <input
        class="form-check-input mt-0 me-1"
        type="checkbox"
        value=""
        aria-label="Checkbox for following text input"
      />
      <label>Writing</label>
    </div>
  </div>

  <div class="d-none">
  <div class="form-check form-check-inline">
    <label :for="`incomplete-${student.item_id}`" :title="incompleteTitle">
      <input
        type="checkbox"
        name="incomplete"
        value="1"
        :id="`incomplete-${student.item_id}`"
        :disabled="!student.allows_incomplete"
        :checked="student.has_incomplete"
      />
      <strong><span aria-hidden="true">I</span></strong>
    </label>
  </div>
  <div>
    <span v-if="student.has_incomplete">Default</span>
    <input
      type="text"
      aria-label=""
      aria-expanded="true"
      aria-autocomplete="list"
      aria-owns="owned_listbox"
      aria-activedescendant="selected_option"
      aria-required="true"
      :id="`grade-${student.item_id}`"
      :value="student.no_grade_now ? `X (No grade now)` : student.grade"
      :disabled="student.is_submitted"
    />
  </div>
  <div v-if="!student.is_writing_section">
    <label :for="`writing-${student.item_id}`" :title="writingTitle">
      <input
        type="checkbox"
        name="writing_credit"
        value="1"
        :id="`writing-${student.item_id}`"
        :disabled="!student.allows_writing_credit"
        :checked="student.has_writing_credit"
      />
      <strong><span aria-hidden="true">W</span></strong>
    </label>
  </div>
</div>
</template>

<script>
export default {
  props: {
    student: {
      type: Object,
      required: true,
    },
  },
  computed: {
    incompleteTitle() {
      return this.student.allows_incomplete
        ? ""
        : "Incomplete not allowed for " +
            this.student.student_firstname +
            " " +
            this.student.student_lastname;
    },
    writingTitle() {
      return this.student.allows_writing_credit
        ? ""
        : "Writing Credit not allowed for " +
            this.student.student_firstname +
            " " +
            this.student.student_lastname;
    },
  },
};
</script>
