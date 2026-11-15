#version 330 core
// V5 candidate: original, NASA-2007-inspired cinematic ignition.
// A visual metaphor for cosmological expansion, NOT an explosion into space.
// Preserve exact original 18-22 s image by fading this overlay to alpha 0 at t>=18.
in vec2 TexCoords;
out vec4 FragColor;
uniform float uTime, uAspect;

float hash21(vec2 p) {
    p = fract(p * vec2(123.34,345.45));
    p += dot(p,p+34.345);
    return fract(p.x*p.y);
}
float noise2(vec2 p) {
    vec2 i=floor(p), f=fract(p);
    f=f*f*(3.0-2.0*f);
    return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),
               mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
float fbm2(vec2 p) {
    return .54*noise2(p)+.27*noise2(p*2.03+13.8)+
           .13*noise2(p*4.11-4.7)+.06*noise2(p*8.23+23.7);
}
float ss(float a,float b,float x) { return smoothstep(a,b,x); }

void main() {
    float t=max(0.0,uTime);
    vec2 uv=TexCoords*2.0-1.0;
    uv.x*=uAspect;
    // Gentle cinematic push without moving the originating world-space point.
    float r=length(uv), ang=atan(uv.y,uv.x);
    float build=ss(0.0,3.8,t);
    vec3 light=vec3(0.0);

    // A legible small seed against pure black for the opening beats.
    float origin=exp(-r*r/(0.000030+0.00028*build));
    light+=origin*vec3(1.42,1.08,1.90)*(1.2+2.65*build);
    light+=exp(-8.5*r)*vec3(0.31,0.11,0.62)*(0.18+0.85*build);

    // Asymmetric optical rays during ignition. The original flare stays
    // on-screen, but the pure geometric wheel is broken up with turbulence.
    float ignition=ss(2.5,4.15,t)*(1.0-ss(8.5,10.5,t));
    float distort=fbm2(vec2(ang*3.2,t*0.11))-0.5;
    float rayPattern=pow(abs(cos(ang*4.0+distort*0.23)),36.0);
    float rays=rayPattern*exp(-3.35*r)*ss(.015,.085,r)*ignition;
    light+=vec3(.94,.66,1.42)*rays*1.60;

    // A single rapidly growing, irregular energy/radiation front. The
    // low-frequency angular displacement makes this a non-circular bloom;
    // fine density variations create coherent folds, not disconnected rings.
    float swell=ss(3.2,10.2,t);
    float shellR=.04+1.20*swell;
    float angleWarp=fbm2(vec2(ang*2.8+8.4,t*.105))-0.5;
    float radWarp=fbm2(uv*3.4+vec2(t*.045,-t*.036))-0.5;
    float contour=shellR*(0.77+0.40*(angleWarp+.5))+0.075*radWarp;
    float thick=mix(.055,.29,swell);
    float dd=(r-contour)/max(thick,.001);
    float shell=exp(-dd*dd*1.70);
    float contourDetail=fbm2(vec2(ang*7.0+r*1.8,t*.17-r*2.4));
    float fissure=ss(.29,.73,contourDetail);
    float frontGate=ss(3.20,4.1,t)*(1.0-ss(10.8,13.0,t));
    vec3 shellCol=mix(vec3(.48,.14,.84),vec3(1.18,.64,1.48),fissure);
    light+=shellCol*shell*frontGate*(0.28+1.25*fissure);

    // Hot shredded interior. Swirling, multi-scale material is advected
    // continuously to prevent temporal flicker at 30fps.
    float inside=1.0-ss(contour-.18,contour+.15,r);
    vec2 flow=uv*(2.55+.52*swell);
    flow+=vec2(0.17*sin(uv.y*3.7+t*.20),0.13*cos(uv.x*3.1-t*.17));
    float low=fbm2(flow+vec2(t*.038,-t*.027));
    float hi=fbm2(uv*9.0+vec2(t*.075,-t*.060));
    float ridges=ss(.36,.69,low+.14*(hi-.5));
    float matter=inside*ss(3.8,5.3,t)*(1.0-ss(11.5,14.7,t));
    vec3 iridescent=mix(vec3(.13,.07,.39),vec3(.70,.35,.87),ridges);
    iridescent=mix(iridescent,vec3(1.06,.72,.89),pow(ridges,3.0)*.52);
    light+=matter*iridescent*(.23+1.05*ridges);

    // Broader high-key expanding medium, but with distinct purple/cyan
    // shadowed folds, leaving local negative space instead of grey whiteout.
    float cloudGate=ss(6.25,9.0,t)*(1.0-ss(14.1,17.5,t));
    vec2 drift=vec2(.023*t,-.016*t);
    float broad=fbm2(uv*2.40+drift+vec2(7.4,3.2));
    float medium=fbm2(uv*5.85+drift*.83+vec2(11.2,-2.7));
    float micro=fbm2(uv*13.6+drift*1.60+vec2(-3.5,9.1));
    float cloudDensity=ss(.34,.70,broad*.68+medium*.28+micro*.12);
    float veil=ss(.22,.71,broad);
    float cold=ss(.40,.70,medium);
    vec3 cloudColor=mix(vec3(.095,.10,.22),vec3(.60,.65,.80),veil);
    cloudColor=mix(cloudColor,vec3(.72,.52,.88),cold*.40);
    light+=cloudColor*cloudDensity*cloudGate*1.25;

    // V6/V7: perceptible violet-white climax of the ignition followed by
    // an immediate smooth falloff into the continuous expansion field.
    // The brighter optical effect is an original artistic metaphor.
    float flash=exp(-pow(abs((t-5.90)/0.55),4.0));
    light+=vec3(2.2,2.1,2.35)*exp(-2.1*r)*flash*2.3;
    light+=vec3(1.2,1.1,1.3)*exp(-0.9*r*r)*flash*1.2;

    // Preserve the approved V4 native 18-22s handoff EXACTLY: after
    // t=18 there is no V5 contribution. No other film epochs are changed.
    float cover=1.0-ss(14.5,18.0,t);
    FragColor=vec4(max(light,vec3(0.0)),cover);
}
