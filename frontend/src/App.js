import { useState } from "react";
import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const field =
  "mt-1.5 w-full rounded-xl border border-zinc-200 bg-white px-3 py-2.5 text-sm text-zinc-900 shadow-sm transition placeholder:text-zinc-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20";
const label = "text-xs font-semibold uppercase tracking-wide text-zinc-500";
const checkLabel =
  "flex cursor-pointer gap-3 rounded-xl border border-zinc-100 bg-zinc-50/80 px-3 py-2.5 text-sm leading-snug text-zinc-800";

function BoolRow({ id, checked, onToggle, children }) {
  return (
    <label htmlFor={id} className={checkLabel}>
      <input
        id={id}
        type="checkbox"
        className="mt-0.5 h-4 w-4 shrink-0 rounded border-zinc-300 text-indigo-600 focus:ring-indigo-500/30"
        checked={checked}
        onChange={onToggle}
      />
      <span>{children}</span>
    </label>
  );
}

const STEP_TITLES = [
  "Driver profile",
  "Vehicle & maintenance",
  "Usage & locations",
  "Behaviour & environment",
  "Roads & time patterns",
  "Past accident severity",
];

function App() {
  const [primaryCityOrRegion, setPrimaryCityOrRegion] = useState("");
  const [additionalPlaceKeywords, setAdditionalPlaceKeywords] = useState("");
  const [driverAge, setDriverAge] = useState("");
  const [gender, setGender] = useState("Male");
  const [yearsLicensed, setYearsLicensed] = useState("");
  const [vehicleType, setVehicleType] = useState("Car");
  const [vehicleAge, setVehicleAge] = useState("");
  const [areaType, setAreaType] = useState("Urban");
  const [usageType, setUsageType] = useState("Private");
  const [priorClaims, setPriorClaims] = useState("");
  const [engineCapacityCc, setEngineCapacityCc] = useState("");
  const [vehicleValue, setVehicleValue] = useState("");
  const [annualDistanceKm, setAnnualDistanceKm] = useState("");
  const [loading, setLoading] = useState(false);
  const [riskClass, setRiskClass] = useState("");
  const [finalScore, setFinalScore] = useState(null);
  const [components, setComponents] = useState(null);
  const [riskIndicators, setRiskIndicators] = useState([]);
  const [activeFlag, setActiveFlag] = useState("");
  const [recommendation, setRecommendation] = useState("");
  const [error, setError] = useState("");
  const [decisionExplanation, setDecisionExplanation] = useState(null);
  const [kbMetrics, setKbMetrics] = useState(null);

  const [step, setStep] = useState(1);
  const totalSteps = STEP_TITLES.length;

  const [tyreCondition, setTyreCondition] = useState("good");

  const defaultExposureFlags = {
    vehicle_brake_issues_known: false,
    typical_speeding: false,
    typical_drunk_driving_risk: false,
    typical_phone_distraction: false,
    typical_reckless_or_overtake: false,
    typical_driver_fatigue: false,
    typical_heavy_rain: false,
    typical_fog: false,
    typical_strong_wind: false,
    typical_poor_visibility: false,
    typical_darkness_low_light: false,
    typical_wet_slippery_roads: false,
    often_highway_driving: false,
    often_intersections_junctions: false,
    often_heavy_traffic_congestion: false,
    often_rural_roads: false,
    often_drive_at_night: false,
    often_peak_hour_travel: false,
    often_off_peak_travel: false,
    mostly_daytime_driving: false,
    past_accident_injury: false,
    past_accident_fatality_involved: false,
    past_multi_vehicle_accident: false,
  };
  const [exposureFlags, setExposureFlags] = useState(defaultExposureFlags);
  const toggleExposure = (key) => setExposureFlags((f) => ({ ...f, [key]: !f[key] }));

  const getRiskColorClasses = (risk) => {
    if (risk === "Critical") return "bg-red-950 text-red-50 ring-1 ring-red-900/40";
    if (risk === "Very High") return "bg-red-50 text-red-900 ring-1 ring-red-300/80";
    if (risk === "High") return "bg-orange-50 text-orange-900 ring-1 ring-orange-200/80";
    if (risk === "Medium") return "bg-amber-50 text-amber-900 ring-1 ring-amber-200/80";
    return "bg-emerald-50 text-emerald-900 ring-1 ring-emerald-200/80";
  };

  const flagDetails = {
    speeding: {
      description: "Excessive speed detected.",
      level: "High",
      premiumImpact: "Usually increases premium due to higher future claim likelihood.",
    },
    drunk_driving: {
      description: "Alcohol influence detected.",
      level: "High",
      premiumImpact: "Can significantly raise premium and trigger strict underwriting review.",
    },
    rain: {
      description: "Wet road conditions detected.",
      level: "Medium",
      premiumImpact: "May moderately increase premium due to reduced road grip risk.",
    },
    darkness: {
      description: "Low visibility conditions.",
      level: "Medium",
      premiumImpact: "Can increase premium because nighttime visibility raises claim probability.",
    },
    night_driving: {
      description: "Increased night risk.",
      level: "Medium",
      premiumImpact: "May cause moderate loading because night driving has higher incident rates.",
    },
    brake_failure: {
      description: "Mechanical failure detected.",
      level: "High",
      premiumImpact: "Often leads to higher premium due to severe vehicle safety concerns.",
    },
    junction: {
      description: "High risk road location.",
      level: "Medium",
      premiumImpact: "Can add moderate premium loading from higher collision frequency areas.",
    },
    highway: {
      description: "High speed road detected.",
      level: "Medium",
      premiumImpact: "May increase premium due to high-speed impact severity.",
    },
  };

  const getFlagDetail = (flag) =>
    flagDetails[flag] ?? {
      description: "Indicator from place keywords or structured answers.",
      level: "Low",
      premiumImpact: "May have a minor impact on premium after underwriter review.",
    };

  const toNumber = (value) => Number.parseInt(value || "0", 10);
  const toFloat = (value) => Number.parseFloat(value || "0") || 0;
  const normalizeFlag = (flag) => flag.toLowerCase().replaceAll(" ", "_");

  const handleAssessRisk = async () => {
    setLoading(true);
    setError("");
    setRiskClass("");
    setFinalScore(null);
    setComponents(null);
    setRiskIndicators([]);
    setActiveFlag("");
    setRecommendation("");
    setDecisionExplanation(null);
    setKbMetrics(null);

    try {
      const response = await axios.post(`${API_BASE}/api/assess`, {
        primary_city_or_region: primaryCityOrRegion.trim(),
        additional_place_keywords: additionalPlaceKeywords.trim(),
        accident_history_narrative: "",
        driver_age: toNumber(driverAge),
        gender,
        years_licensed: toNumber(yearsLicensed),
        vehicle_type: vehicleType,
        vehicle_age: toNumber(vehicleAge),
        engine_capacity_cc: Math.max(0, toNumber(engineCapacityCc)),
        vehicle_value: Math.max(0, toFloat(vehicleValue)),
        annual_distance_km: Math.max(0, toNumber(annualDistanceKm)),
        area_type: areaType,
        usage_type: usageType,
        prior_claims: Math.max(0, toNumber(priorClaims)),
        tyre_condition: tyreCondition,
        ...exposureFlags,
      });

      const risk = response?.data?.policyholder_risk_class ?? "";
      const score = Number(response?.data?.predicted_claim_risk_score ?? 0);
      const safeScore = Number.isFinite(score) ? Math.max(0, Math.min(100, score)) : 0;
      const rawComponents = response?.data?.component_breakdown ?? {};
      const safeComponents = {
        behavioural: Number.isFinite(Number(rawComponents?.behavioural))
          ? Math.max(0, Math.min(100, Number(rawComponents.behavioural)))
          : 0,
        environmental: Number.isFinite(Number(rawComponents?.environmental))
          ? Math.max(0, Math.min(100, Number(rawComponents.environmental)))
          : 0,
        time: Number.isFinite(Number(rawComponents?.time))
          ? Math.max(0, Math.min(100, Number(rawComponents.time)))
          : 0,
        vehicle: Number.isFinite(Number(rawComponents?.vehicle))
          ? Math.max(0, Math.min(100, Number(rawComponents.vehicle)))
          : 0,
        location: Number.isFinite(Number(rawComponents?.location))
          ? Math.max(0, Math.min(100, Number(rawComponents.location)))
          : 0,
        claims_severity: Number.isFinite(Number(rawComponents?.claims_severity))
          ? Math.max(0, Math.min(100, Number(rawComponents.claims_severity)))
          : 0,
      };
      const responseIndicators = Array.isArray(response?.data?.risk_indicators)
        ? response.data.risk_indicators
        : [];
      const responseRecommendation = response?.data?.underwriting_recommendation ?? "";
      const explanation = response?.data?.risk_decision_explanation ?? null;
      const metrics = response?.data?.risk_decision_explanation?.metrics ?? null;

      setRiskClass(risk);
      setFinalScore(safeScore);
      setComponents(safeComponents);
      setRiskIndicators(responseIndicators);
      setActiveFlag("");
      setRecommendation(responseRecommendation);
      setDecisionExplanation(explanation);
      setKbMetrics(metrics);
    } catch {
      setError("Could not reach the API. Is the backend running on port 8000?");
      setRiskClass("");
      setFinalScore(null);
      setComponents(null);
      setRiskIndicators([]);
      setActiveFlag("");
      setRecommendation("");
      setDecisionExplanation(null);
      setKbMetrics(null);
    } finally {
      setLoading(false);
    }
  };

  const riskColorClasses = getRiskColorClasses(riskClass);
  const componentLabels = [
    { key: "behavioural", label: "Behavioural" },
    { key: "environmental", label: "Environmental" },
    { key: "time", label: "Time" },
    { key: "vehicle", label: "Vehicle" },
    { key: "location", label: "Location" },
    { key: "claims_severity", label: "Claims / severity" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-100 via-white to-zinc-100">
      <div className="mx-auto max-w-5xl px-4 py-10 md:px-6 lg:py-14">
        <header className="mb-10 text-center md:text-left">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">Motor underwriting</p>
          <h1 className="mt-2 text-balance text-3xl font-bold tracking-tight text-zinc-900 md:text-4xl">
            Policyholder risk assessor
          </h1>
          <p className="mx-auto mt-3 max-w-2xl text-pretty text-sm leading-relaxed text-zinc-600 md:mx-0">
            Standardized underwriting form first; optional placenames match your gazette against accident texts in{" "}
            <span className="font-mono text-xs">knowledge/</span> so frequent places (e.g. Mutare) can lift calibration.
          </p>
        </header>

        <div className="grid gap-8 lg:grid-cols-12 lg:items-start">
          <section className="rounded-2xl border border-zinc-200/90 bg-white p-6 shadow-soft lg:col-span-7 lg:p-8">
            <h2 className="text-sm font-semibold text-zinc-900">Motor insurance risk assessment</h2>
            <p className="mt-1 text-xs leading-relaxed text-zinc-500">
              Walk through driver profile, vehicle, usage, declared exposure (behaviour, weather, roads, time, past
              severity—aligned with accident-report features in your System Doc), then placenames for knowledge-base
              matching. Checkboxes map into the risk-rule dimensions on the backend.
            </p>

            <div className="mt-5 mb-2">
              <div className="flex justify-between text-xs font-medium text-zinc-600">
                <span>
                  Step {step} of {totalSteps}
                </span>
                <span className="text-indigo-700">{STEP_TITLES[step - 1]}</span>
              </div>
              <div className="mt-2 flex gap-1">
                {STEP_TITLES.map((t, i) => (
                  <div
                    key={t}
                    title={t}
                    className={`h-1.5 min-w-0 flex-1 rounded-full transition-colors ${i < step ? "bg-indigo-600" : "bg-zinc-200"}`}
                  />
                ))}
              </div>
            </div>

            {step === 1 && (
              <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="driver-age" className={label}>
                    Driver age
                  </label>
                  <input
                    id="driver-age"
                    type="number"
                    inputMode="numeric"
                    value={driverAge}
                    onChange={(e) => setDriverAge(e.target.value)}
                    className={field}
                    placeholder="e.g. 34"
                  />
                </div>
                <div>
                  <label htmlFor="gender" className={label}>
                    Gender
                  </label>
                  <select id="gender" value={gender} onChange={(e) => setGender(e.target.value)} className={field}>
                    <option>Male</option>
                    <option>Female</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="years-licensed" className={label}>
                    Years licensed (driving experience)
                  </label>
                  <input
                    id="years-licensed"
                    type="number"
                    inputMode="numeric"
                    value={yearsLicensed}
                    onChange={(e) => setYearsLicensed(e.target.value)}
                    className={field}
                  />
                </div>
                <div>
                  <label htmlFor="prior-claims" className={label}>
                    Prior claims (claims history)
                  </label>
                  <input
                    id="prior-claims"
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={priorClaims}
                    onChange={(e) => setPriorClaims(e.target.value)}
                    className={field}
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="vehicle-type" className={label}>
                    Vehicle type
                  </label>
                  <select id="vehicle-type" value={vehicleType} onChange={(e) => setVehicleType(e.target.value)} className={field}>
                    <option>Car</option>
                    <option>Truck</option>
                    <option>Motorcycle</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="vehicle-age" className={label}>
                    Vehicle age (years)
                  </label>
                  <input
                    id="vehicle-age"
                    type="number"
                    inputMode="numeric"
                    value={vehicleAge}
                    onChange={(e) => setVehicleAge(e.target.value)}
                    className={field}
                  />
                </div>
                <div>
                  <label htmlFor="engine-cc" className={label}>
                    Engine capacity (cc)
                  </label>
                  <input
                    id="engine-cc"
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={engineCapacityCc}
                    onChange={(e) => setEngineCapacityCc(e.target.value)}
                    className={field}
                    placeholder="e.g. 1600"
                  />
                </div>
                <div>
                  <label htmlFor="vehicle-value" className={label}>
                    Vehicle value (book currency)
                  </label>
                  <input
                    id="vehicle-value"
                    type="number"
                    min={0}
                    step="any"
                    inputMode="decimal"
                    value={vehicleValue}
                    onChange={(e) => setVehicleValue(e.target.value)}
                    className={field}
                    placeholder="e.g. 12000"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label htmlFor="tyre-condition" className={label}>
                    Tyre condition (vehicle / tyre condition)
                  </label>
                  <select
                    id="tyre-condition"
                    value={tyreCondition}
                    onChange={(e) => setTyreCondition(e.target.value)}
                    className={field}
                  >
                    <option value="good">Good</option>
                    <option value="fair">Fair / worn</option>
                    <option value="poor">Poor / replace soon</option>
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <BoolRow
                    id="vehicle_brake_issues_known"
                    checked={exposureFlags.vehicle_brake_issues_known}
                    onToggle={() => toggleExposure("vehicle_brake_issues_known")}
                  >
                    Known brake issues or prior brake-related incident (brake failure risk factor)
                  </BoolRow>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="annual-km" className={label}>
                    Annual distance travelled (km)
                  </label>
                  <input
                    id="annual-km"
                    type="number"
                    min={0}
                    inputMode="numeric"
                    value={annualDistanceKm}
                    onChange={(e) => setAnnualDistanceKm(e.target.value)}
                    className={field}
                    placeholder="e.g. 18000"
                  />
                </div>
                <div>
                  <label htmlFor="area-type" className={label}>
                    Area (urban vs rural)
                  </label>
                  <select id="area-type" value={areaType} onChange={(e) => setAreaType(e.target.value)} className={field}>
                    <option>Urban</option>
                    <option>Rural</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="usage-type" className={label}>
                    Usage type (private vs commercial)
                  </label>
                  <select id="usage-type" value={usageType} onChange={(e) => setUsageType(e.target.value)} className={field}>
                    <option>Private</option>
                    <option>Commercial</option>
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <label htmlFor="primary-city" className={label}>
                    Primary city or region (optional — knowledge-base gazette match)
                  </label>
                  <input
                    id="primary-city"
                    type="text"
                    value={primaryCityOrRegion}
                    onChange={(e) => setPrimaryCityOrRegion(e.target.value)}
                    placeholder="e.g. Mutare, Harare"
                    className={field}
                  />
                </div>
                <div className="sm:col-span-2">
                  <label htmlFor="place-keywords" className={label}>
                    Roads, suburbs, or landmarks (optional)
                  </label>
                  <input
                    id="place-keywords"
                    type="text"
                    value={additionalPlaceKeywords}
                    onChange={(e) => setAdditionalPlaceKeywords(e.target.value)}
                    placeholder="e.g. Bulawayo Road, CBD, highway to airport"
                    className={field}
                  />
                  <p className="mt-2 text-xs leading-relaxed text-zinc-500">
                    Short text only—used to match your gazette against accident files in knowledge/, not a free-text claim
                    narrative.
                  </p>
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="mt-6 grid gap-6 md:grid-cols-2">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Driver behaviour</p>
                  <p className="mt-1 text-[11px] text-zinc-500">
                    Typical patterns (speeding, DUI risk, phone, reckless overtaking, fatigue)
                  </p>
                  <div className="mt-3 space-y-2">
                    <BoolRow id="typical_speeding" checked={exposureFlags.typical_speeding} onToggle={() => toggleExposure("typical_speeding")}>
                      Speeding or excessive speed is typical for this driver
                    </BoolRow>
                    <BoolRow
                      id="typical_drunk_driving_risk"
                      checked={exposureFlags.typical_drunk_driving_risk}
                      onToggle={() => toggleExposure("typical_drunk_driving_risk")}
                    >
                      Alcohol / drunk-driving risk factors apply
                    </BoolRow>
                    <BoolRow
                      id="typical_phone_distraction"
                      checked={exposureFlags.typical_phone_distraction}
                      onToggle={() => toggleExposure("typical_phone_distraction")}
                    >
                      Distracted driving (e.g. mobile phone use)
                    </BoolRow>
                    <BoolRow
                      id="typical_reckless_or_overtake"
                      checked={exposureFlags.typical_reckless_or_overtake}
                      onToggle={() => toggleExposure("typical_reckless_or_overtake")}
                    >
                      Reckless driving or dangerous overtaking
                    </BoolRow>
                    <BoolRow
                      id="typical_driver_fatigue"
                      checked={exposureFlags.typical_driver_fatigue}
                      onToggle={() => toggleExposure("typical_driver_fatigue")}
                    >
                      Driver fatigue / sleepiness in typical trips
                    </BoolRow>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Environment</p>
                  <p className="mt-1 text-[11px] text-zinc-500">Rain, fog, wind, visibility, darkness, wet roads</p>
                  <div className="mt-3 space-y-2">
                    <BoolRow id="typical_heavy_rain" checked={exposureFlags.typical_heavy_rain} onToggle={() => toggleExposure("typical_heavy_rain")}>
                      Often drives in heavy rain
                    </BoolRow>
                    <BoolRow id="typical_fog" checked={exposureFlags.typical_fog} onToggle={() => toggleExposure("typical_fog")}>
                      Often in fog / mist
                    </BoolRow>
                    <BoolRow id="typical_strong_wind" checked={exposureFlags.typical_strong_wind} onToggle={() => toggleExposure("typical_strong_wind")}>
                      Often strong wind exposure
                    </BoolRow>
                    <BoolRow
                      id="typical_poor_visibility"
                      checked={exposureFlags.typical_poor_visibility}
                      onToggle={() => toggleExposure("typical_poor_visibility")}
                    >
                      Poor visibility (glare, smoke, dust, etc.)
                    </BoolRow>
                    <BoolRow
                      id="typical_darkness_low_light"
                      checked={exposureFlags.typical_darkness_low_light}
                      onToggle={() => toggleExposure("typical_darkness_low_light")}
                    >
                      Darkness / low-light driving is common
                    </BoolRow>
                    <BoolRow
                      id="typical_wet_slippery_roads"
                      checked={exposureFlags.typical_wet_slippery_roads}
                      onToggle={() => toggleExposure("typical_wet_slippery_roads")}
                    >
                      Wet or slippery roads are common on usual routes
                    </BoolRow>
                  </div>
                </div>
              </div>
            )}

            {step === 5 && (
              <div className="mt-6 grid gap-6 md:grid-cols-2">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Road & location patterns</p>
                  <p className="mt-1 text-[11px] text-zinc-500">Highway, junctions, congestion, rural roads</p>
                  <div className="mt-3 space-y-2">
                    <BoolRow
                      id="often_highway_driving"
                      checked={exposureFlags.often_highway_driving}
                      onToggle={() => toggleExposure("often_highway_driving")}
                    >
                      Often on highways / high-speed roads
                    </BoolRow>
                    <BoolRow
                      id="often_intersections_junctions"
                      checked={exposureFlags.often_intersections_junctions}
                      onToggle={() => toggleExposure("often_intersections_junctions")}
                    >
                      Often at intersections / junctions
                    </BoolRow>
                    <BoolRow
                      id="often_heavy_traffic_congestion"
                      checked={exposureFlags.often_heavy_traffic_congestion}
                      onToggle={() => toggleExposure("often_heavy_traffic_congestion")}
                    >
                      Often in heavy traffic / congestion
                    </BoolRow>
                    <BoolRow id="often_rural_roads" checked={exposureFlags.often_rural_roads} onToggle={() => toggleExposure("often_rural_roads")}>
                      Often on rural roads
                    </BoolRow>
                  </div>
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Time of travel</p>
                  <p className="mt-1 text-[11px] text-zinc-500">Daytime, night, peak, off-peak</p>
                  <div className="mt-3 space-y-2">
                    <BoolRow id="mostly_daytime_driving" checked={exposureFlags.mostly_daytime_driving} onToggle={() => toggleExposure("mostly_daytime_driving")}>
                      Mostly daytime driving
                    </BoolRow>
                    <BoolRow id="often_drive_at_night" checked={exposureFlags.often_drive_at_night} onToggle={() => toggleExposure("often_drive_at_night")}>
                      Often drives at night
                    </BoolRow>
                    <BoolRow
                      id="often_peak_hour_travel"
                      checked={exposureFlags.often_peak_hour_travel}
                      onToggle={() => toggleExposure("often_peak_hour_travel")}
                    >
                      Often during peak hours
                    </BoolRow>
                    <BoolRow
                      id="often_off_peak_travel"
                      checked={exposureFlags.often_off_peak_travel}
                      onToggle={() => toggleExposure("often_off_peak_travel")}
                    >
                      Often off-peak / quiet hours
                    </BoolRow>
                  </div>
                </div>
              </div>
            )}

            {step === 6 && (
              <div className="mt-6 space-y-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Accident severity history</p>
                <p className="text-[11px] leading-relaxed text-zinc-500">
                  Past incidents involving injuries, fatalities, or multiple vehicles (maps to severity dimension). Only
                  tick what genuinely applies.
                </p>
                <div className="space-y-2">
                  <BoolRow
                    id="past_accident_injury"
                    checked={exposureFlags.past_accident_injury}
                    onToggle={() => toggleExposure("past_accident_injury")}
                  >
                    Past accident(s) involved injuries
                  </BoolRow>
                  <BoolRow
                    id="past_accident_fatality_involved"
                    checked={exposureFlags.past_accident_fatality_involved}
                    onToggle={() => toggleExposure("past_accident_fatality_involved")}
                  >
                    Past accident involved a fatality (declared)
                  </BoolRow>
                  <BoolRow
                    id="past_multi_vehicle_accident"
                    checked={exposureFlags.past_multi_vehicle_accident}
                    onToggle={() => toggleExposure("past_multi_vehicle_accident")}
                  >
                    Past multi-vehicle accident(s)
                  </BoolRow>
                </div>
              </div>
            )}

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <button
                type="button"
                disabled={step <= 1}
                onClick={() => setStep((s) => Math.max(1, s - 1))}
                className="rounded-xl border border-zinc-200 bg-white px-4 py-2.5 text-sm font-semibold text-zinc-800 shadow-sm transition hover:bg-zinc-50 disabled:pointer-events-none disabled:opacity-40"
              >
                Back
              </button>
              <div className="flex flex-1 justify-end gap-3">
                {step < totalSteps ? (
                  <button
                    type="button"
                    onClick={() => setStep((s) => Math.min(totalSteps, s + 1))}
                    className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md transition hover:bg-indigo-500"
                  >
                    Next
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleAssessRisk}
                    disabled={loading}
                    className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-md transition hover:bg-indigo-500 disabled:pointer-events-none disabled:opacity-40"
                  >
                    {loading ? (
                      <>
                        <span
                          className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
                          aria-hidden
                        />
                        Assessing…
                      </>
                    ) : (
                      "Run risk assessment"
                    )}
                  </button>
                )}
              </div>
            </div>

            {error && (
              <div
                className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
                role="alert"
              >
                {error}
              </div>
            )}
          </section>

          <aside className="lg:col-span-5 lg:sticky lg:top-8">
            {riskClass && finalScore !== null && components ? (
              <div className="space-y-6">
                <div className="rounded-2xl border border-zinc-200/90 bg-white p-6 shadow-glow md:p-7">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Classification</p>
                      <p className="mt-1 text-lg font-semibold text-zinc-900">Policyholder risk</p>
                    </div>
                    <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-bold ${riskColorClasses}`}>
                      {riskClass}
                    </span>
                  </div>

                  <div className="mt-6">
                    <div className="flex justify-between text-xs font-medium text-zinc-600">
                      <span>Predicted claim risk</span>
                      <span className="tabular-nums text-zinc-900">{finalScore}%</span>
                    </div>
                    <div className="mt-2 h-3 overflow-hidden rounded-full bg-zinc-100">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-500"
                        style={{ width: `${finalScore}%` }}
                      />
                    </div>
                  </div>

                  <div className="mt-8 space-y-4">
                    <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Component breakdown</p>
                    {componentLabels.map(({ key, label: lbl }) => (
                      <div key={key}>
                        <div className="flex justify-between text-xs font-medium text-zinc-600">
                          <span>{lbl}</span>
                          <span className="tabular-nums">{components[key]}%</span>
                        </div>
                        <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-zinc-100">
                          <div
                            className="h-full rounded-full bg-indigo-400/90"
                            style={{ width: `${components[key]}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-zinc-200/90 bg-white p-6 shadow-soft md:p-7">
                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Risk indicators</p>
                  {riskIndicators.length > 0 ? (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {riskIndicators.map((flagLabel) => {
                        const flagKey = normalizeFlag(flagLabel);
                        const detail = getFlagDetail(flagKey);
                        return (
                          <div key={flagLabel} className="relative">
                            <button
                              type="button"
                              onClick={() => setActiveFlag((prev) => (prev === flagLabel ? "" : flagLabel))}
                              className="rounded-full bg-zinc-100 px-3 py-1.5 text-xs font-semibold text-zinc-800 ring-1 ring-zinc-200/80 transition hover:bg-zinc-200/80"
                            >
                              {flagLabel}
                            </button>
                            {activeFlag === flagLabel && (
                              <div className="absolute left-0 top-full z-20 mt-2 w-[min(100vw-2rem,18rem)] rounded-xl border border-zinc-200 bg-white p-4 shadow-lg">
                                <p className="text-sm font-semibold text-zinc-900">{flagLabel}</p>
                                <p className="mt-2 text-xs leading-relaxed text-zinc-600">{detail.description}</p>
                                <p className="mt-2 text-xs text-zinc-700">
                                  <span className="font-semibold">Level:</span> {detail.level}
                                </p>
                                <p className="mt-1 text-xs text-zinc-700">
                                  <span className="font-semibold">Premium:</span> {detail.premiumImpact}
                                </p>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p className="mt-2 text-sm text-zinc-500">No major indicators from the lexicon.</p>
                  )}
                </div>

                <div className="rounded-2xl border border-indigo-100 bg-indigo-50/40 p-6 md:p-7">
                  <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700">Underwriting</p>
                  <p className="mt-2 text-sm leading-relaxed text-indigo-950/90">
                    {recommendation || "Assess using standard criteria."}
                  </p>
                </div>

                {decisionExplanation?.sections?.length > 0 && (
                  <div className="rounded-2xl border border-zinc-200/90 bg-white p-6 shadow-soft md:p-7">
                    <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Decision trace</p>
                    <p className="mt-2 text-xs leading-relaxed text-zinc-600">
                      The final score starts from your structured form index, then knowledge-base calibration adjusts each
                      dimension when your optional placenames overlap frequent terms from{" "}
                      <span className="font-mono">data/kb.sqlite</span>.
                    </p>
                    {kbMetrics && (
                      <dl className="mt-4 grid gap-3 rounded-xl border border-indigo-100 bg-indigo-50/50 p-4 text-xs sm:grid-cols-2">
                        <div className="sm:col-span-2">
                          <dt className="text-indigo-800">This submission — form index vs calibrated final</dt>
                          <dd className="mt-1 text-[11px] leading-relaxed text-indigo-950/90">
                            No free-text accident narrative blend: the form produces one index; corpus lifts rescale
                            dimensions when place keywords match your accident files (see Mutare example in the trace
                            sections).
                          </dd>
                        </div>
                        <div>
                          <dt className="text-zinc-500">Structured index (form)</dt>
                          <dd className="mt-0.5 font-semibold tabular-nums text-zinc-900">{kbMetrics.structured_score}</dd>
                        </div>
                        <div>
                          <dt className="text-zinc-500">Before KB → after KB calibration</dt>
                          <dd className="mt-0.5 font-semibold tabular-nums text-zinc-900">
                            {kbMetrics.form_index_before_kb ?? kbMetrics.nlp_raw} →{" "}
                            {kbMetrics.final_after_kb_calibration ?? kbMetrics.nlp_adjusted}
                          </dd>
                        </div>
                        <div>
                          <dt className="text-zinc-500">Gazette spans (place fields)</dt>
                          <dd className="mt-0.5 font-semibold tabular-nums text-zinc-900">
                            {kbMetrics.gazette_match_count ?? "—"}
                          </dd>
                        </div>
                        <div className="sm:col-span-2">
                          <dt className="text-zinc-500">Place text preview</dt>
                          <dd className="mt-0.5 text-[11px] text-zinc-700">
                            {kbMetrics.form_kb_text_preview ? `"${kbMetrics.form_kb_text_preview}"` : "—"}
                          </dd>
                        </div>
                        {kbMetrics.components_raw_nlp &&
                          typeof kbMetrics.components_raw_nlp === "object" &&
                          Object.keys(kbMetrics.components_raw_nlp).length > 0 && (
                            <div className="sm:col-span-2">
                              <dt className="text-zinc-500">Dimension baselines (underwriting + declared exposure, before corpus lift)</dt>
                              <dd className="mt-1 font-mono text-[11px] leading-relaxed text-zinc-800">
                                {Object.entries(kbMetrics.components_raw_nlp)
                                  .map(([k, v]) => `${k} ${v}`)
                                  .join(" · ")}
                              </dd>
                            </div>
                          )}
                      </dl>
                    )}
                    {kbMetrics && (
                      <dl className="mt-4 grid gap-3 rounded-xl border border-zinc-100 bg-zinc-50/80 p-4 text-xs sm:grid-cols-2">
                        <div className="sm:col-span-2">
                          <dt className="font-medium text-zinc-700">Knowledge base (corpus calibration)</dt>
                          <dd className="mt-1 text-[11px] text-zinc-500">
                            Real-accident files build phrase frequencies; when you type the same placenames in the form,
                            frequent corpus terms (e.g. Mutare) increase calibration on the matching dimension.
                          </dd>
                        </div>
                        <div className="sm:col-span-2">
                          <dt className="text-zinc-500">Corpus snapshot</dt>
                          <dd className="mt-0.5 font-semibold text-zinc-900">
                            {kbMetrics.kb_document_count} docs
                            {kbMetrics.kb_aggregate_run_id != null && (
                              <span className="ml-2 font-normal text-zinc-500">run #{kbMetrics.kb_aggregate_run_id}</span>
                            )}
                          </dd>
                          {Array.isArray(kbMetrics.kb_source_documents) && kbMetrics.kb_source_documents.length > 0 && (
                            <dd className="mt-2 flex flex-wrap gap-1.5">
                              {kbMetrics.kb_source_documents.slice(0, 10).map((n) => (
                                <span
                                  key={n}
                                  className="rounded-md bg-white px-2 py-0.5 font-mono text-[10px] text-zinc-700 ring-1 ring-zinc-200"
                                >
                                  {n}
                                </span>
                              ))}
                              {kbMetrics.kb_source_documents.length > 10 && (
                                <span className="text-zinc-400">+{kbMetrics.kb_source_documents.length - 10} more</span>
                              )}
                            </dd>
                          )}
                        </div>
                        {kbMetrics.kb_corpus_category_lifts &&
                          typeof kbMetrics.kb_corpus_category_lifts === "object" &&
                          Object.keys(kbMetrics.kb_corpus_category_lifts).length > 0 && (
                            <div className="sm:col-span-2">
                              <dt className="text-zinc-500">Category prevalence lifts (corpus dimensions)</dt>
                              <dd className="mt-1 font-mono text-[11px] leading-relaxed text-zinc-800">
                                {Object.entries(kbMetrics.kb_corpus_category_lifts)
                                  .map(([k, v]) => `${k}×${v}`)
                                  .join(" · ")}
                              </dd>
                            </div>
                          )}
                        {kbMetrics.kb_term_prevalence_lifts &&
                          typeof kbMetrics.kb_term_prevalence_lifts === "object" &&
                          Object.keys(kbMetrics.kb_term_prevalence_lifts).length > 0 && (
                            <div className="sm:col-span-2">
                              <dt className="text-zinc-500">Term prevalence lifts (matched phrases common in corpus)</dt>
                              <dd className="mt-1 font-mono text-[11px] leading-relaxed text-zinc-800">
                                {Object.entries(kbMetrics.kb_term_prevalence_lifts)
                                  .map(([k, v]) => `${k}×${v}`)
                                  .join(" · ")}
                              </dd>
                            </div>
                          )}
                        {kbMetrics.kb_lifts && Object.keys(kbMetrics.kb_lifts).length > 0 && (
                          <div className="sm:col-span-2">
                            <dt className="text-zinc-500">Effective combined lift (applied to narrative components)</dt>
                            <dd className="mt-1 font-mono text-[11px] leading-relaxed text-zinc-800">
                              {Object.entries(kbMetrics.kb_lifts)
                                .map(([k, v]) => `${k}×${v}`)
                                .join(" · ")}
                            </dd>
                          </div>
                        )}
                      </dl>
                    )}
                    {(() => {
                      const sections = decisionExplanation.sections;
                      const submission = sections.filter((s) => s.group === "submission" || !s.group);
                      const kbOnly = sections.filter((s) => s.group === "knowledge_base");
                      const outcome = sections.filter((s) => s.group === "outcome");
                      const renderBlock = (title, accent, items) =>
                        items.length > 0 ? (
                          <div>
                            <p className={`text-[11px] font-semibold uppercase tracking-wide ${accent}`}>{title}</p>
                            <ul className="mt-3 space-y-4">
                              {items.map((s) => (
                                <li key={s.title}>
                                  <p className="text-sm font-semibold text-zinc-900">{s.title}</p>
                                  <p className="mt-1 text-sm leading-relaxed text-zinc-600">{s.detail}</p>
                                </li>
                              ))}
                            </ul>
                          </div>
                        ) : null;
                      return (
                        <div className="mt-6 space-y-8 border-t border-zinc-100 pt-6">
                          {renderBlock(
                            "Your assessment (this submission)",
                            "text-emerald-800",
                            submission,
                          )}
                          {renderBlock("Knowledge base", "text-amber-800", kbOnly)}
                          {renderBlock("Outcome", "text-indigo-800", outcome)}
                        </div>
                      );
                    })()}
                  </div>
                )}
              </div>
            ) : (
              <div className="rounded-2xl border border-dashed border-zinc-300 bg-zinc-50/50 p-8 text-center md:p-10">
                <p className="text-sm font-medium text-zinc-700">Results appear here</p>
                <p className="mt-2 text-xs leading-relaxed text-zinc-500">
                  Complete all steps and run the assessment. Connect the backend first (
                  <span className="font-mono">uvicorn</span> on port 8000).
                </p>
              </div>
            )}
          </aside>
        </div>
      </div>
    </div>
  );
}

export default App;
