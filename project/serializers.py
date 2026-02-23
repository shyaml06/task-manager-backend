import rest_framework.serializers as serializers




class ProjectSerializer(serializers.Serializer):

    name = serializers.CharField(
        max_length=200,
        allow_blank=False
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True
    )

    start_date = serializers.DateField()

    end_date = serializers.DateField(
        required=False,
        allow_null=True
    )

    # ✅ Custom validation
    def validate(self, data):

        start = data.get("start_date")
        end = data.get("end_date")

        if end and end < start:
            raise serializers.ValidationError(
                "End date cannot be before start date"
            )

        return data
    
class TaskSerializer(serializers.Serializer):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    project_id = serializers.IntegerField(min_value=1)

    title = serializers.CharField(
        max_length=200
    )

    description = serializers.CharField(
        required=False,
        allow_blank=True
    )

    status = serializers.ChoiceField(
        choices=STATUS_CHOICES,
        default="pending"
    )

    due_date = serializers.DateField(
        required=False,
        allow_null=True
    )

    def validate_project_id(self, value):
        from .services import project_exists

        if not project_exists(value):
            raise serializers.ValidationError("Invalid project")

        return value







    
    
    
    
    
    