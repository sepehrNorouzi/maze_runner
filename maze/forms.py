from django import forms
from maze.models import Maze

class SimpleMazeForm(forms.Form):
    """Alternative simple form without ModelForm"""

    algorithm = forms.ChoiceField(
        choices=Maze.GrowingTreeAlgoType.choices,
        initial=Maze.GrowingTreeAlgoType.NEWEST,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Algorithm"
    )

    width = forms.IntegerField(
        min_value=10,
        initial=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter width (10-500)'
        }),
        label="Width"
    )

    height = forms.IntegerField(
        min_value=10,
        initial=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter height (10-500)'
        }),
        label="Height"
    )

    hybrid_prob = forms.FloatField(
        min_value=0.0,
        max_value=1.0,
        initial=0.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Enter probability (0.0-1.0)'
        }),
        label="Hybrid Probability"
    )

    def clean(self):
        cleaned_data = super().clean()
        algorithm = cleaned_data.get('algorithm')
        hybrid_prob = cleaned_data.get('hybrid_prob')

        if algorithm != Maze.GrowingTreeAlgoType.HYBRID and hybrid_prob > 0:
            raise forms.ValidationError(
                "Hybrid probability should be 0.0 when not using Hybrid algorithm"
            )

        if algorithm == Maze.GrowingTreeAlgoType.HYBRID and hybrid_prob == 0:
            raise forms.ValidationError(
                "Hybrid probability must be greater than 0.0 when using Hybrid algorithm"
            )

        return cleaned_data
