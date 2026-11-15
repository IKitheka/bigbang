#version 330 core
// Original independently computed opening, art-directed against the user's
// NASA SVS 10128 (2007) reference. A science-fiction-like violet-white
// point and short luminous transition are deliberate *cinematic metaphors*:
// no claim that a literal photographed singularity or explosion existed.
in vec2 TexCoords;
out vec4 FragColor;
uniform float uTime,uAspect;

float h21(vec2 p) {
    p=fract(p*vec2(123.34,345.45));
    p+=dot(p,p+34.345);
    return fract(p.x*p.y);
}
float n2(vec2 p) {
    vec2 i=floor(p), f=fract(p);
    f=f*f*(3.0-2.0*f);
    return mix(mix(h21(i),h21(i+vec2(1,0)),f.x),
               mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x),f.y);
}
float fm2(vec2 p) {
    return 0.56*n2(p)+0.28*n2(p*2.07+9.7)+
           0.12*n2(p*4.13-14.2)+0.04*n2(p*8.29+5.1);
}

void main() {
    float t=max(0.0,uTime);
    vec2 uv=TexCoords*2.0-vec2(1.0);
    uv.x*=uAspect;
    float r=length(uv);
    float theta=atan(uv.y,uv.x);

    // 0–3s: very small violet-white point on black, with a soft optical halo.
    float build=smoothstep(0.0,3.3,t);
    float core=exp(-r*r/(0.000045+0.00042*build))*(1.4+3.5*build);
    float halo=exp(-12.0*r)*(0.10+0.7*build);
    vec3 light=vec3(0.43,0.12,0.70)*halo+
               vec3(1.35,0.92,1.80)*core;

    // 3–7s: eight diffraction-style lavender-white spikes bloom outward.
    // Optical spikes are stylization, not literal jets into empty space.
    float burst=smoothstep(2.2,4.2,t)*
                (1.0-smoothstep(6.5,8.1,t));
    float spikes=pow(abs(cos(theta*4.0+0.10)),27.0)*
                 exp(-r*5.1)*smoothstep(0.004,0.065,r);
    float rays=spikes*burst*1.85;
    light+=vec3(0.67,0.47,0.93)*rays;
    light+=vec3(0.55,0.28,0.81)*
           exp(-3.7*r)*burst*0.23;

    // A short purposeful high-key transition, as actually present in NASA's
    // chosen reference around 2.7s of its 14s film. Limit it temporally.
    float flash=exp(-pow(abs((t-6.95)/0.82),4.0));
    light+=vec3(1.34,1.39,1.53)*flash;

    // 8–16s: wide pale medium with soft 2D projected optical variations.
    // This represents visual continuity with the later true volumetric
    // transport scene, not a solved QGP or cosmological density field.
    float cloudWeight=smoothstep(7.5,9.5,t)*
                      (1.0-smoothstep(13.7,17.9,t));
    vec2 drift=vec2(t*0.008,-t*0.004);
    float broad=fm2(uv*3.3+drift+vec2(3.5,1.4));
    float fine=fm2(uv*10.7+drift*2.0+vec2(6.8,-2.1));
    float layers=0.35+0.70*smoothstep(0.27,0.78,broad)+
                 0.10*(fine-0.5);
    vec3 cloud=vec3(0.70,0.73,0.78)*layers*cloudWeight;
    light+=cloud;

    // Blend into the previously owner-liked true 3D primordial volume.
    // Fully ZERO by 18 seconds so all 18–22s protected images match exactly.
    float cover=1.0-smoothstep(14.5,18.0,t);
    FragColor=vec4(max(light,vec3(0.0)),cover);
}
