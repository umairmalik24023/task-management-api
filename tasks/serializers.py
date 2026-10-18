
from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "due_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Title cannot be empty."
            )

        return value

    def validate_priority(self, value):
        if not 0 <= value <= 3:
            raise serializers.ValidationError(
                "Priority must be between 0 and 3."
            )

        return value


class TaskFilterSerializer(serializers.Serializer):
    # Validates query parameters used to filter and search tasks.
    # Unlike ModelSerializer, this class does not represent a database model.

    status = serializers.ChoiceField(
        choices=Task.Status.choices,  # Only allow statuses defined in the Task model.
        required=False,               # The client can omit this filter.
    )

    priority = serializers.IntegerField(
        min_value=0,  # Reject priorities below 0.
        max_value=3,  # Reject priorities above 3.
        required=False,
    )

    search = serializers.CharField(
        required=False,       # Searching is optional.
        allow_blank=True,     # Allow an empty search string.
        trim_whitespace=True, # Remove whitespace from the beginning and end.
        max_length=200,       # Reject search strings longer than 200 characters.
    )
    
    """
    Let's understand one important thing.

    TaskSerializer handles validation and serialization of task data when creating, updating, or reading tasks.

    TaskFilterSerializer validates query parameters used to filter and search tasks.
    
    One important distinction: We didn't move all the view's logic into the serializer. We moved the input validation rules. The view still applies the filters to the database and returns the paginated response.

    That is the separation of concerns we're aiming for! 💪

    """
    
    