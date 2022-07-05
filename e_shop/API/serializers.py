from rest_framework import serializers

CEFR_CHOICES = (
    ("A1", "Beginner"),
    ("A2", "Elementary"),
    ("B1", "Intermediate"),
    ("B2", "Upper-Intermediate"),
    ("C1", "Advanced"),
    ("C2", "Proficiency")
)

SEX_CHOICES = (
    ("M", "Male"),
    ("F", "Female")
)


class CandidateCefrSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=30, min_length=2)
    sex = serializers.ChoiceField(choices=SEX_CHOICES)
    age = serializers.IntegerField(min_value=16)
    eng_level = serializers.ChoiceField(choices=CEFR_CHOICES)
    
    def validate(self, data):
        validated_data = super().validate(data)
        sex = validated_data.get("sex")
        age = validated_data.get("age")
        eng_level = validated_data.get("eng_level")
        
        admission_male = sex == "M" and age >= 20 and eng_level in ["C1", "C2"]
        admission_female = sex == "F" and age > 22 and eng_level in ["B2", "C1", "C2"]
        
        if not (admission_male or admission_female):
            raise serializers.ValidationError \
                ("Sorry, your questionnaire does not match the search criteria")
        return data

# from e_shop.API.serializers import CandidateCefrSerializer
# import io
# from rest_framework.parsers import JSONParser
# stream = io.BytesIO(b'{"name": "Alex", "sex": "M", "age": "27", "eng_level": "C1"}')
# data = JSONParser().parse(stream)
# serializer = CandidateCefrSerializer(data=data)
# serializer.is_valid(raise_exception=True)
# serializer.validated_data
