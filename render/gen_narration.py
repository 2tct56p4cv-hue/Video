import json, subprocess, os, wave, contextlib

SC = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.join(SC, "audio")
VOICE_DIR = os.path.join(SC, "voice")
# one narrator per capability; intro and closing share the "host" voice
VOICES = {
  "s1": "en-us-ryan-medium",
  "s2": "en-us-amy-low",
  "s3": "en-gb-alan-low",
  "s4": "en-gb-southern_english_female-low",
  "s5": "en-us-lessac-medium",
  "s6": "en-us-kathleen-low",
  "s7": "en-us-danny-low",
  "s8": "en-us-amy-low",
  "s9": "en-us-ryan-medium",
}
os.makedirs(AUD, exist_ok=True)

scenes = [
  ("s1", "Behind every successful technology transformation, there is a team of specialists working together. Data engineers and analysts who turn information into insight. Software and cloud engineers who build the solutions. Test managers and QA automation specialists who make sure everything works. DevOps and platform engineers who deliver it faster. Risk and governance specialists who keep it trustworthy. And migration and delivery leads who bring it all safely into production. That is our Technology Team."),
  ("s2", "Our Data Engineers and Data Analysts turn complex information into something businesses can actually use. We build reliable data pipelines, improve data quality, and transform large volumes of financial data into trusted insights. From SQL and Python to BigQuery, GCP, dbt and Airflow, we help move data from complexity to business value."),
  ("s3", "Our engineers build the technology behind those insights. We develop applications, integrations, and cloud-native solutions designed for modern financial institutions. Whether we are working with Java, Python, microservices, or cloud platforms such as AWS, Azure, and Google Cloud, the objective is the same: solutions that are scalable, secure, and resilient."),
  ("s4", "But building something is only part of the journey. Our Test Managers and QA Automation specialists make sure solutions actually work, reliably, securely, and at scale. From test strategy and automation to performance testing and QA leadership, we identify problems before they become business problems."),
  ("s5", "Our DevOps and platform specialists connect development with delivery. We automate pipelines, implement GitOps processes, and help organizations modernize legacy technology. The result is faster delivery, more resilient platforms, and less manual complexity."),
  ("s6", "In financial services, however, technology also needs trust. Our specialists combine technology expertise with knowledge of AML, transaction monitoring, data governance, data quality, and regulatory requirements. We help ensure that the right data is available, the right controls are in place, and transformation remains compliant."),
  ("s7", "And when organizations need to move from legacy technology to something new, our migration and delivery expertise helps make that change possible. We coordinate complex migrations, cutovers, and transformation activities so that technology, data, and people arrive at the destination together, with minimal disruption to the business."),
  ("s8", "The real strength of the team is not any single technology or role. It is how these capabilities connect. Data Engineering works with Analytics. Developers work with Cloud and DevOps. Testing protects delivery. Governance creates trust. And migration expertise helps bring everything safely into the real world."),
  ("s9", "We may come from different technical backgrounds, but we share one objective: using technology to solve real problems and create better outcomes for our clients. Different skills. Connected expertise. One Technology Team."),
]

def wav_duration(path):
    with contextlib.closing(wave.open(path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

# extra breathing room per scene: (lead-in before VO starts, hold after VO ends)
pad = {
    "s1": (2.5, 4.5),
    "s2": (2.0, 4.5),
    "s3": (2.0, 4.5),
    "s4": (2.0, 7.0),   # extra hold for the silent bug gag
    "s5": (2.0, 4.5),
    "s6": (2.0, 4.5),
    "s7": (2.0, 4.5),
    "s8": (2.0, 5.0),
    "s9": (2.2, 7.0),   # extra hold for the closing card
}

timeline = []
t = 0.0

for sid, text in scenes:
    raw = os.path.join(AUD, f"{sid}_raw.wav")
    subprocess.run(
        ["python3", "-m", "piper", "-m", os.path.join(VOICE_DIR, VOICES[sid] + ".onnx"), "-f", raw],
        input=text.encode("utf-8"),
        check=True,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    dur = wav_duration(raw)
    lead_in, hold = pad[sid]
    start = t
    vo_start = start + lead_in
    vo_end = vo_start + dur
    end = vo_end + hold
    timeline.append({
        "id": sid,
        "start": round(start, 3),
        "voStart": round(vo_start, 3),
        "voDur": round(dur, 3),
        "voEnd": round(vo_end, 3),
        "end": round(end, 3),
    })
    t = end

total = t

with open(os.path.join(SC, "timeline.json"), "w") as f:
    json.dump({"scenes": timeline, "total": round(total, 3)}, f, indent=2)

print(json.dumps({"total": round(total,3), "scenes": timeline}, indent=2))
