#!/usr/bin/env python3
"""Generate an ORIGINAL, deterministic five-minute cinematic stereo score.

No copyrighted recording, sound library, song, or generative model is used.
Everything is synthesized from elementary oscillators, amplitude envelopes
and seeded noise. The sound is a soundtrack to a silent-space *visualization*,
not a claim that explosions or galaxies transmit sound in a vacuum.

Requires: python3-numpy (Ubuntu apt). Outputs a plain 32kHz stereo PCM WAV
for reproducible remuxing with FFmpeg AAC in the release workflow.
"""
from __future__ import annotations
import argparse
import math
import pathlib
import wave

import numpy as np

SAMPLE_RATE = 32000
DURATION_SECONDS = 300


def smooth(a: float, b: float, t: np.ndarray) -> np.ndarray:
    x = np.clip((t - a) / (b - a), 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def impact(t: np.ndarray, moment: float, gain: float = 1.0) -> np.ndarray:
    age = t - moment
    positive = np.maximum(age, 0.0)
    active = (age >= 0.0).astype(np.float64)
    bass = np.sin(2.0 * np.pi *
                  (34.0 * positive + 31.0 * np.log1p(positive * 4.0)))
    tail = np.sin(2.0 * np.pi *
                  (55.0 * positive + 3.4 * positive * positive))
    return active * gain * (
        0.165 * bass * np.exp(-positive * 1.7) +
        0.045 * tail * np.exp(-positive * 0.55))


def bell(t: np.ndarray, when: float, freq: float, intensity: float) -> np.ndarray:
    age = t - when
    active = (age >= 0.0).astype(np.float64)
    p = np.maximum(age, 0.0)
    env = (1.0 - np.exp(-p * 22.0)) * np.exp(-p * 0.85)
    sig = (np.sin(2.0 * np.pi * freq * age) +
           0.18 * np.sin(2.0 * np.pi * 2.01 * freq * age) +
           0.07 * np.sin(2.0 * np.pi * 3.99 * freq * age))
    return active * intensity * env * sig


def score(t: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    # Dramatic dark D-minor-ish overtone structure, continuous deterministic
    # phase/frequency modulation without reinitialising phases per one-second
    # chunk (prevents audible click at audio-chunk boundaries).
    rise = smooth(0.2, 8.0, t)
    darkness = 1.0 - 0.79 * smooth(80.0, 83.0, t) * (
        1.0 - smooth(87.0, 92.0, t))
    late = smooth(87.0, 105.0, t)
    solar = smooth(113.0, 144.0, t)
    final_fade = 1.0 - smooth(293.0, 300.0, t)

    # Low warm sub-drone + rich slow chorus.
    undulate = 0.72 + 0.28 * np.sin(2.0*np.pi*0.061*t) ** 2
    drone = (0.073*np.sin(2*np.pi*(55.0*t+0.42*np.sin(2*np.pi*0.09*t))) +
             0.048*np.sin(2*np.pi*(82.407*t+0.17*np.sin(2*np.pi*0.11*t))) +
             0.026*np.sin(2*np.pi*110.0*t) +
             0.015*np.sin(2*np.pi*164.81*t))
    drone *= rise * darkness * undulate * (0.50+0.45*late)

    # Opening: delicate expectancy then wide cinematic ignition.
    origin_env = (1.0 - smooth(8.0, 18.0, t))
    origin = origin_env * (
        0.038*np.sin(2*np.pi*(220.0*t+2.0*np.sin(t*0.11))) +
        0.020*np.sin(2*np.pi*329.63*t)*smooth(3.0, 7.0, t))
    winds = smooth(2.5, 7.0, t)*(1.0-smooth(8.0,15.0,t))
    sweep = 0.043*winds*np.sin(2*np.pi*(160.0*t+0.16*t*t))

    # Hot / opaque matter: textured gentle pulse without a literal "space
    # explosion" claim or arbitrary rhythmic jump cuts.
    matter = smooth(35.0, 48.0, t)*(1.0-smooth(70.0,80.0,t))
    pulse = (0.50+0.50*np.cos(2*np.pi*0.28*t))**4
    plasma = matter * pulse * (
        0.045*np.sin(2*np.pi*(41.2*t+0.35*np.sin(t*1.17))) +
        0.023*np.sin(2*np.pi*123.47*t))

    # Post-recombination, distant star birth: shimmering stable harmonics.
    stars = late * (1.0-smooth(115.0,135.0,t))
    air = stars*(0.020*np.sin(2*np.pi*(196.0*t+0.18*np.sin(t*0.17)))+
                 0.012*np.sin(2*np.pi*293.66*t)+
                 0.009*np.sin(2*np.pi*392.00*t))

    # V12 extended solar-formation arc in original C-major-ish palette.
    solar_pad = solar * (
        0.043*np.sin(2*np.pi*130.81*t) +
        0.032*np.sin(2*np.pi*196.00*t) +
        0.031*np.sin(2*np.pi*261.63*t) +
        0.025*np.sin(2*np.pi*329.63*t))
    melody = np.zeros_like(t)
    notes = [261.63,329.63,392.0,523.25,392.0,329.63,440.0,523.25,
             659.25,523.25,392.0,329.63]
    for i,freq in enumerate(notes):
        melody += bell(t, 145.0+12.4*i, freq, 0.031)

    # Original quiet granular tones accumulate with the visible clumps.
    accretion = np.zeros_like(t)
    for i in range(13):
        accretion += bell(t, 178.0+5.2*i, 392.0+29.0*(i%5), 0.008)
    build = smooth(112.0,132.0,t)*(1.0-smooth(140.0,153.0,t))
    accretion += build*0.018*np.sin(2*np.pi*(98.0*t+0.05*t*t))
    # Gentle resolution begins with the actual 283-second Earth camera move.
    resolution = bell(t,283.0,261.63,0.032)+bell(t,286.0,329.63,0.027)+bell(t,289.0,392.0,0.023)
    # Low-frequency musical accents follow cinematic formation milestones.
    impacts=np.zeros_like(t)
    for moment,gain in [(6.9,1.35),(35.0,0.38),(50.0,0.25),
                        (65.0,0.22),(80.0,0.16),(87.0,0.23),
                        (132.0,0.40),(145.0,0.18),(184.0,0.16),
                        (215.0,0.18),(250.0,0.22),(283.0,0.18)]:
        impacts += impact(t,moment,gain)

    # Wide, soft, per-channel synthesized airflow.
    # The random sequence is seeded once; the gate follows the shot cadence.
    noise_amp = (0.0018+0.0040*winds+0.0026*matter+
                 0.0010*stars+0.0012*solar)*final_fade
    left_noise=rng.standard_normal(t.shape)*noise_amp
    right_noise=rng.standard_normal(t.shape)*noise_amp

    centered=(drone+origin+sweep+plasma+air+solar_pad+melody+impacts+accretion+resolution)*final_fade
    stereo_motion=0.08*np.sin(2*np.pi*0.034*t)
    left=centered*(1.0+stereo_motion)+left_noise
    right=centered*(1.0-stereo_motion)+right_noise
    return left,right


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=pathlib.Path,required=True)
    parser.add_argument("--seconds",type=int,default=DURATION_SECONDS)
    args=parser.parse_args()
    if not 1<=args.seconds<=DURATION_SECONDS:
        parser.error("--seconds must be 1..300")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(20261115)
    peak=0.0
    with wave.open(str(args.output),"wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        for sec in range(args.seconds):
            t=sec+np.arange(SAMPLE_RATE,dtype=np.float64)/SAMPLE_RATE
            left,right=score(t,rng)
            samples=np.column_stack((left,right))
            peak=max(peak,float(np.max(np.abs(samples))))
            if peak>0.98: raise RuntimeError(f"Original score would clip: {peak}")
            encoded=np.round(np.clip(samples,-1.0,1.0)*32767.0)
            w.writeframes(encoded.astype("<i2").tobytes())
    with wave.open(str(args.output),"rb") as w:
        assert w.getnframes()==args.seconds*SAMPLE_RATE
        assert w.getnchannels()==2
    print(f"Original stereo cinematic soundtrack, {args.seconds}s @ "
          f"{SAMPLE_RATE}Hz, measured peak {peak:.3f}; output {args.output}")


if __name__=="__main__":
    main()
