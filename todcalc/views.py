# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections
from decimal import Decimal
from django.shortcuts import render
from .forms import TODCalcForm
from .models import UsageOnRangeModel

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = TODCalcForm(request.POST, request.FILES)
        if form.is_valid():
            # Parse XML and load into model for processing
            data = UsageOnRangeModel(request.FILES['usage_data_file'])
            result = data.calculate(
                tod_plan=1 if form.cleaned_data['tod_plan'] == 'dr1' else 2,
                baseline_kwh=form.cleaned_data['baseline_kilowatt_hour'],
                percentage_chg_per_all_hrs=form.cleaned_data['percentage_change_across_all_hours']/Decimal(100),
                percentage_chg_per_peak_hr=form.cleaned_data['percentage_change_across_peak_hours']/Decimal(100),
                use_avg_usage=True if form.cleaned_data['percentage_change_relative_to'] == 'avg' else False)
            result_no_chg = data.calculate(
                tod_plan=0,
                baseline_kwh=form.cleaned_data['baseline_kilowatt_hour'],
                percentage_chg_per_all_hrs=0,
                percentage_chg_per_peak_hr=0,
                use_avg_usage=True)
    else:
        form = TODCalcForm()
        result = {}
        result_no_chg = {}

    result = collections.OrderedDict(sorted(result.items()))
    result_no_chg = collections.OrderedDict(sorted(result_no_chg.items()))
    return render(request, 'todcalc.html', {
        'form': form, 
        'sum_result': sum([i[1].cost for i in result.iteritems()]), 
        'result': result, 
        'sum_result_no_chg': sum([i[1].cost for i in result_no_chg.iteritems()]),
        'result_no_chg': result_no_chg})
