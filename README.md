# SDG&E Time of Day cost calculator tool

I wrote this in a single evening to help me determine whether I should opt out
of my local utility's conversion of its customers to Time of Use plans
(https://www.sdge.com/whenmatters). This code is definitely not production
quality but it should work well enough to give one a general idea as to how much
extra/less their bills will be depending on the provided input.

## Instructions

1. Install Django and Python if not already installed.
2. python manage.py runserver
3. Go to http://localhost:8080/todcalc/ in your browser and provide the following input:
   - Baseline kilowatt hour (from your bill)
   - The desired ToD plan
   - The percentage change in usage across all hours of the day (positive values reduce usage, negative values increase)
   - The percentage change in usage across peak hours (+ = reduction, - = increase)
   - "Percentage change relative to" -- this effectively caps peak usage changes
     to one of the selected options. For example, if the lowest usage was at 3am
     on a given day (0.5 kWh) and 2 kWh was used at 7pm, a 25% reduction would reduce
     usage at 7pm by 0.375 kWh (1.625 kWh).
   - The XML file extracted from the ZIP file provided by the Green Button
     Download tool on your online account.

## Maybe for future development

- Ability to redistribute some peak usage to off/super off peak periods
- Differing summer/winter baseline usage values
