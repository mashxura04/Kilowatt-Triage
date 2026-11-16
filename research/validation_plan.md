# Validation plan

**Status: this is a plan only.** No real-school energy data has been collected and no validation against real schools has been done. Nothing in this document should be presented as a result.

## 1. What has and has not been checked

| Already done (software and source checks) | Not done (needs real-school data) |
|---|---|
| All 24 savings and cost values in `data/retrofit_data.csv` match World Bank (2021) Tables 42 and 47. | Does the reference-school energy use resemble real Uzbek schools? |
| Baseline intensities and totals match Tables 36 and 37. | Are retrofit savings really proportional to floor area? |
| The report's boiler savings match its stated percentages applied to heating demand after insulation (all four zones, within 1 kWh). | Do real boiler and insulation upgrades deliver the modelled savings? |
| 203 automated tests pass. | Are 2021 reference costs, and their scaling with floor area, realistic? |

Matching the report shows the software reproduces the report. It does **not** show the report's model matches real schools.

## 2. Claims to test, and the evidence each needs

| Model output | Question | Evidence needed |
|---|---|---|
| Baseline heating, lighting and equipment intensity (kWh/m²/yr) per climate zone | Is the reference school typical? | 12 to 36 months of energy bills, floor area, local degree days |
| Savings scaled linearly with floor area | Is saving per m² similar across school sizes? | Several schools of different sizes, measured before/after |
| Insulation saving | Is the modelled reduction achieved? | Heating energy before and after, weather-normalised |
| Boiler saving as a percentage of post-insulation demand | Does a boiler upgrade cut fuel use by the modelled share? | Fuel records before/after, boiler efficiency check by a qualified technician |
| LED saving (about 3.7 kWh/m²/yr in the model) | Is the lighting saving realistic? | Lamp inventory, wattage, operating hours |
| 2021 costs, and area-proportional scaling of them | What do retrofits actually cost for schools of different sizes? | Quotes and invoices: date, scope, floor area |
| Compatibility rules and "needs review" flags | Are they technically sensible? | Review by a qualified energy or mechanical engineer |

## 3. Data to collect from each school

**A. Building**: gross floor area, number of floors, year built, wall and roof construction, window type, existing insulation, photographs of the buildings only (no people).

**B. Heating system**: type and fuel, boiler capacity (kW), age, nameplate efficiency, condition, operating season dates, how it is controlled.

**C. Energy use** (at least 12 months, ideally 36; monthly if possible):
- Coal: tonnes purchased, delivery dates, stock left at season start and end.
- Gas: meter readings (m³). Electricity: kWh. District heat: Gcal if applicable.
- Unit prices actually paid.
- For every fuel, the supplier's stated energy content, so quantities can be converted to kWh. Record the source of each conversion figure.

**D. Operation**: pupils and staff, school calendar and closures, evening or community use, thermostat set-points, known cold rooms.

**E. Lighting**: lamp type, count, wattage, daily hours.

**F. Electrical capacity**: main breaker rating, supply transformer details if known, spare capacity (needed for any fuel-switch assessment).

**G. Weather**: monthly outdoor temperature from the nearest weather station, converted to heating degree days with the base temperature stated.

**H. Retrofit costs**: any quote or invoice for insulation, boiler, lighting, with date, scope and area.

## 4. Useful measurements (if equipment and permission allow)

- Indoor temperature and humidity loggers, 2 to 4 per school, for at least 4 weeks in the heating season.
- Lighting: sample lamp wattage with a plug-in meter; hours from a logger or the caretaker's schedule.
- Boiler efficiency: flue-gas analysis by a qualified technician only.
- Electrical peak demand: utility data or a measurement by a qualified electrician.

**Safety:** team members must not open boilers or electrical panels. Use qualified staff for anything beyond reading meters and bills.

## 5. How to compare model and reality

1. **Clean the data.** Check units, gaps and estimated bills. Note anything unusual.
2. **Normalise.** Express energy as kWh/m²/yr. Adjust heating for the year's weather using degree days.
3. **Baseline check.** For each school, compare measured intensity with the model value for its climate zone. Show all schools, not only the average. Report error per school, average bias and spread.
4. **Allow for under-heating.** Many schools are not heated to comfort level, so measured use can be lower than modelled demand. Check indoor temperatures before calling a difference a model error.
5. **Savings check.** Use before/after data of at least 12 months each, weather-normalised (the whole-building approach in the IPMVP protocol). For lighting, measure wattage and hours directly. If a school installs several measures together, compare the result with the modelled sequential package, not with the sum of separate figures.
6. **Cost check.** Plot actual retrofit cost against floor area for each measure and test whether cost per m² is roughly constant. This decides whether area-proportional cost scaling is defensible.
7. **Agree the pass/fail thresholds before looking at the data**, and write them down. ASHRAE Guideline 14 (monthly NMBE within ±5% and CV(RMSE) up to 15%) is the usual benchmark for calibrated building models. This project is a screening tool, not a calibrated simulation, so looser thresholds will be needed; whatever is chosen must be justified and disclosed.
8. **Keep some schools aside.** Do not adjust the model using the same schools used to claim it is validated.

## 6. Phases and what we may claim

| Phase | Work | Claim allowed afterwards |
|---|---|---|
| 0 (done) | Software tests and source checks | "The software reproduces the World Bank figures." |
| 1 | 3 to 5 pilot schools, ideally across different climate zones: bills and the checklist above | "For *n* schools, measured intensity was / was not consistent with the model baseline." State *n*. |
| 2 | Measurements in the heating season, collection of cost data | "Measured indoor temperatures and lighting loads were ..." and the first cost-versus-area evidence |
| 3 | Before/after data from any school that is retrofitted (may fall outside the project timeline) | Savings claims, only for those schools |

A handful of schools cannot be called representative of Uzbekistan. Say so.

## 7. Permissions and ethics

Ask the school administration (and the relevant education authority if required) for written permission. Keep school names out of public material unless agreed. Store data securely. Do not photograph pupils.

## 8. Limitations to state in the final presentation

- The model is built on one World Bank reference school; it is not measured data from any school.
- No validation against real energy bills or measurements has been done yet.
- Savings are scaled proportionally with floor area, which is an assumption.
- Costs are 2021 reference values for the reference school and are not scaled to the evaluated school's floor area.
- Boiler savings are applied after insulation. This matches the report's numbers but the report does not state the sequence in words.
- Fuel-switch options (electric boiler, heat pump) have no calculated net saving because their extra electricity use is not documented.
- Heating-system condition does not change any estimate.
- The budget optimizer only chooses between a few fixed packages.
- Results are preliminary estimates, not an engineering assessment.

## 9. Results table template (one row per school)

| School ID | Zone | Area (m²) | Heating fuel | Months of data | Measured heating (kWh/m²/yr) | Model heating (kWh/m²/yr) | Error (%) | Mean indoor temp (°C) | Notes |
|---|---|---|---|---|---|---|---|---|---|