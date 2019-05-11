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
    baseline_kilowatt_hour = forms.IntegerField(label=u"Baseline kWh", initial=275, help_text="""
(Can be found on a recent SDG&E bill or by clicking <a href="https://www.sdge.com/baseline-allowance-calculator" target="_blank">here</a>.)<br/><br/>
""")
    tod_plan = forms.ChoiceField(widget=forms.RadioSelect(), choices=TOD_PLAN_CHOICE, label="Time of Day plan to compare against", initial="dr1")
    percentage_change_across_all_hours = forms.IntegerField(label="Percentage change across all hours", initial="5", help_text="""
(The percentage amount you're planning on reducing your electric usage by, applied to each hour. Applied before the peak reduction below.)<br/><br/>
""")
    percentage_change_across_peak_hours = forms.IntegerField(label="Percentage change across peak hours (4-9pm)", initial="20", help_text="""
(The percentage amount you're planning on reducing your peak electric usage by on top of the previous reduction. Calculated by the following:<br/><br/>

usage at X PM = usage at X PM - (usage at X PM - cap) * percentage)<br/><br/>

cap is either (usage at 3PM + usage at 9PM) / 2 or the lowest hourly usage for the day, depending on the next choice.)<br/><br/>
""")
    percentage_change_relative_to = forms.ChoiceField(widget=forms.RadioSelect(), choices=RELATIVE_TO_CHOICE, label="Cap decreases to", initial="avg")
    usage_data_file = forms.FileField()
