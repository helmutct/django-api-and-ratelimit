from rest_framework import serializers
from .models import Consumer

class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = '__all__'

    def to_representation(self, instance):
        # Convert model instance to GeoJSON format
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [instance.lng, instance.lat]
            },
            "properties": {
                "id": instance.id,
                "amount_due": instance.amount_due,
                "previous_jobs_count": instance.previous_jobs_count,
                "status": instance.status,
                "street": instance.street
            }
        }
