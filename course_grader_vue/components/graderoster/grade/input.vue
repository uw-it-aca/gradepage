<template>
  <div>
    <label
      :for="`incomplete-${student.item_id}`"
      :title="incompleteTitle"
      >
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
    <label
      :for="`writing-${student.item_id}`"
      :title="writingTitle"
      >
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
      return this.student.allows_incomplete ? "" :
        "Incomplete not allowed for " + this.student.student_firstname +
        " " +  this.student.student_lastname;
    },
    writingTitle() {
      return this.student.allows_writing_credit ? "" :
        "Writing Credit not allowed for " + this.student.student_firstname +
        " " + this.student.student_lastname;
    },
  },
};
</script>
