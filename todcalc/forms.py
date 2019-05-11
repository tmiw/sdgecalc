from django import forms

TOD_PLAN_CHOICE = (
    ('dr1', 'TOD-DR1'),
    ('dr2', 'TOD-DR2')
)

RELATIVE_TO_CHOICE = (
    ('lowest-day', 'Hour with lowest energy usage'),
    ('avg', 'Average of 3pm and 9pm usage')
)

class TODCalcForm(forms.Form):
    baseline_kilowatt_hour = forms.IntegerField(label=u"Baseline kWh", initial=275)
    tod_plan = forms.ChoiceField(widget=forms.RadioSelect(), choices=TOD_PLAN_CHOICE, label="Time of Day plan to compare against", initial="dr1")
    percentage_change_across_all_hours = forms.IntegerField(label="Percentage change across all hours", initial="5")
    percentage_change_across_peak_hours = forms.IntegerField(label="Percentage change across peak hours (4-9pm)", initial="20")
    percentage_change_relative_to = forms.ChoiceField(widget=forms.RadioSelect(), choices=RELATIVE_TO_CHOICE, label="Cap decreases to", initial="avg")
    usage_data_file = forms.FileField()
