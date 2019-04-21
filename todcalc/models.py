# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import xml.etree.ElementTree as ET
from datetime import datetime, date
from decimal import Decimal, getcontext

# Create your models here.
class UsageCostModel:
    def __init__(self, date, cost):
        self.cost = cost
        self.date = date
        self.date_str = self.date.strftime("%m/%Y")

class UsageOnHourModel:
    def __init__(self, kwh):
        self.kwh = kwh

class UsageOnDayModel:
    def __init__(self, date):
        self.date = date
        self.hours = [UsageOnHourModel(0) for i in range(0,24)]

    def cost_at_hour(self, hr, kwh, wh_tier, tod_plan):
        summer_start = date(self.date.year, 6, 1)
        summer_end = date(self.date.year, 10, 31)
        is_summer = self.date >= summer_start and self.date <= summer_end
        is_weekday = self.date.weekday() >= 0 and self.date.weekday() <= 5
        march_or_april = self.date.month == 3 or self.date.month == 4
        is_on_peak = hr >= 16 and hr < 21
        if tod_plan == 1:
            is_super_off_peak = (is_weekday and hr >= 0 and hr < 6) or (is_weekday and march_or_april and hr >= 10 and hr < 14) or (not is_weekday and hr >= 0 and hr < 14)
        else:
            is_super_off_peak = False
        is_off_peak = not is_on_peak and not is_super_off_peak

        if tod_plan == 0:
            if wh_tier == 0 and is_summer: cents_per_kwh = 0.25
            elif wh_tier == 0 and not is_summer: cents_per_kwh = 0.23
            elif wh_tier == 1 and is_summer: cents_per_kwh = 0.44
            elif wh_tier == 1 and not is_summer: cents_per_kwh = 0.41
            elif wh_tier == 2 and is_summer: cents_per_kwh = 0.52
            elif wh_tier == 2 and not is_summer: cents_per_kwh = 0.48
        elif tod_plan == 1:
            if is_summer:
                if wh_tier == 0 and is_on_peak: cents_per_kwh = 0.43
                elif wh_tier == 1 and is_on_peak: cents_per_kwh = 0.62
                elif wh_tier == 0 and is_off_peak: cents_per_kwh = 0.21
                elif wh_tier == 1 and is_off_peak: cents_per_kwh = 0.40
                elif wh_tier == 0 and is_super_off_peak: cents_per_kwh = 0.16
                elif wh_tier == 1 and is_super_off_peak: cents_per_kwh = 0.35
            else:
                if wh_tier == 0 and is_on_peak: cents_per_kwh = 0.25
                elif wh_tier == 1 and is_on_peak: cents_per_kwh = 0.42
                elif wh_tier == 0 and is_off_peak: cents_per_kwh = 0.24
                elif wh_tier == 1 and is_off_peak: cents_per_kwh = 0.41
                elif wh_tier == 0 and is_super_off_peak: cents_per_kwh = 0.22
                elif wh_tier == 1 and is_super_off_peak: cents_per_kwh = 0.40
        elif tod_plan == 2:
            if is_summer:
                if wh_tier == 0 and is_on_peak: cents_per_kwh = 0.40
                elif wh_tier == 1 and is_on_peak: cents_per_kwh = 0.59
                elif wh_tier == 0 and is_off_peak: cents_per_kwh = 0.20
                elif wh_tier == 1 and is_off_peak: cents_per_kwh = 0.39
            else:
                if wh_tier == 0 and is_on_peak: cents_per_kwh = 0.25
                elif wh_tier == 1 and is_on_peak: cents_per_kwh = 0.42
                elif wh_tier == 0 and is_off_peak: cents_per_kwh = 0.23
                elif wh_tier == 1 and is_off_peak: cents_per_kwh = 0.41

        return kwh * Decimal(cents_per_kwh)

    def calculate(self, tod_plan, baseline_kwh, kwh_used_month, percentage_chg_per_all_hrs, percentage_chg_per_peak_hr, use_avg_usage):
        month = date(self.date.year, self.date.month, 1)
        tier1_thresh = baseline_kwh * Decimal("1.3")
        tier2_thresh = baseline_kwh * Decimal(4)  # only used if tod_plan == 0 ("standard plan")

        # set initial tier level
        curtier = 0
        if kwh_used_month[month] > tier1_thresh:
            curtier = 1
            if tod_plan == 0 and kwh_used_month[month] > tier2_thresh:
                curtier = 2

        # apply reduction across all hours
        new_hrs = [Decimal(i.kwh) * (1 - percentage_chg_per_all_hrs) for i in self.hours]

        if use_avg_usage:
            peak_min_cap = (new_hrs[15] + new_hrs[21]) / 2
        else:
            peak_min_cap = min(new_hrs)

        result = Decimal("0.00")
        idx = 0
        for i in new_hrs:
            if idx >= 16 and idx < 21 and tod_plan > 0 and percentage_chg_per_peak_hr > 0:
                amt_to_cut = abs(i - peak_min_cap) * (1 - percentage_chg_per_peak_hr)
                i = i - amt_to_cut

            if (i + kwh_used_month[month]) > tier1_thresh and (tod_plan != 0 or (i + kwh_used_month[month]) <= tier2_thresh) and curtier == 0:
                kwh_new_tier = (i + kwh_used_month[month]) - tier1_thresh
                kwh_old_tier = tier1_thresh - kwh_used_month[month]
                curtier = 1
                result = result + self.cost_at_hour(idx, kwh_old_tier, 0, tod_plan)
                result = result + self.cost_at_hour(idx, kwh_new_tier, 1, tod_plan)
            elif tod_plan == 0 and (i + kwh_used_month[month]) > tier2_thresh:
                kwh_old_tier = tier2_thresh - kwh_used_month[month]
                kwh_new_tier = (i + kwh_used_month[month]) - tier2_thresh
                curtier = 2
                result = result + self.cost_at_hour(idx, kwh_old_tier, 1, tod_plan)
                result = result + self.cost_at_hour(idx, kwh_new_tier, 2, tod_plan)
            else:
                result = result + self.cost_at_hour(idx, i, curtier, tod_plan)

            kwh_used_month[month] = kwh_used_month[month] + i
            idx = idx + 1

        return result

class UsageOnRangeModel:
    def __init__(self, f):
        self.days = {}
        tree = ET.parse(f)
        ns = "{http://www.w3.org/2005/Atom}"
        ns2 = "{http://naesb.org/espi}"
        intervals = tree.findall("{0}entry/{0}content/{1}IntervalBlock/{1}IntervalReading".format(ns, ns2))
        for i in intervals:
            timestamp = i.findall("{0}timePeriod/{0}start".format(ns2))[0].text
            value = i.findall("{0}value".format(ns2))[0].text
            dt = datetime.fromtimestamp(int(timestamp))
            d = dt.date()
            if d in self.days: date_model = self.days[d]
            else:
                date_model = UsageOnDayModel(d)
                self.days[d] = date_model
            date_model.hours[dt.time().hour].kwh = Decimal(value) / Decimal(1000)

    def calculate(self, tod_plan, baseline_kwh, percentage_chg_per_all_hrs, percentage_chg_per_peak_hr, use_avg_usage):
        result = {}
        wh_used_month = {}
        for key in self.days:
            d = date(key.year, key.month, 1)
            if d not in result:
                result[d] = UsageCostModel(d, Decimal(0.00))
                wh_used_month[d] = Decimal("0")
            cost_model = result[d]
            cost_model.cost += self.days[key].calculate(tod_plan, baseline_kwh, wh_used_month, percentage_chg_per_all_hrs, percentage_chg_per_peak_hr, use_avg_usage)
        return result
