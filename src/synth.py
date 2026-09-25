# Sound design for the 15s reel — 120 BPM, A minor. Pure numpy.
import numpy as np, wave
SR=48000; DUR=15.0; N=int(SR*DUR)
rng=np.random.default_rng(3)
dry=np.zeros((N,2)); wet=np.zeros((N,2))
def put(buf,t0,sig,gain=1.0,pan=0.0):
    i=int(t0*SR)
    if sig.ndim==1:
        l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4); sig=np.stack([sig*l*1.414,sig*r*1.414],1)
    j=min(N,i+len(sig))
    if i<0 or i>=N: return
    buf[i:j]+=sig[:j-i]*gain
def T(d): return np.arange(int(d*SR))/SR
def lp(x,cut):  # one-pole lowpass, cut may be array
    cut=np.broadcast_to(np.asarray(cut,float),x.shape)
    a=1-np.exp(-2*np.pi*cut/SR); y=np.empty_like(x); s=0.0
    for k in range(len(x)): s+=a[k]*(x[k]-s); y[k]=s
    return y
def hp(x,cut): return x-lp(x,cut)
# ---- instruments ----
def kick(a=1.0):
    t=T(0.45); f=45+110*np.exp(-t*28); ph=2*np.pi*np.cumsum(f)/SR
    return a*(np.sin(ph)*np.exp(-t*7.5)+0.35*np.exp(-t*250)*rng.standard_normal(len(t))*0.4)
def sub(a=1.0,d=1.4):
    t=T(d); f=30+35*np.exp(-t*6); return a*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*2.2)
def crash(a=1.0,d=1.6):
    t=T(d); n=hp(rng.standard_normal(len(t)),4000); return a*n*np.exp(-t*3.2)
def clap(a=1.0):
    t=T(0.3); n=hp(rng.standard_normal(len(t)),1200); env=np.exp(-t*22)
    for o in (0.008,0.017): env+=np.exp(-np.clip(t-o,0,None)*120)*(t>=o)*.6
    return a*(n*env*.6+0.25*np.sin(2*np.pi*190*t)*np.exp(-t*30))
def hat(a=1.0,d=0.05):
    t=T(d); return a*hp(rng.standard_normal(len(t)),8000)*np.exp(-t*90)
def tick(f=2400,a=1.0,d=0.03):
    t=T(d); return a*np.sin(2*np.pi*f*t)*np.exp(-t*160)
def blip(f0=1400,f1=500,a=1.0,d=0.18):
    t=T(d); f=f1+(f0-f1)*np.exp(-t*30); return a*np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*18)
def saw(freq,t,harm_cut):
    y=np.zeros_like(t)
    for n in range(1,40):
        if n*freq>min(harm_cut,SR/2-1000): break
        y+=np.sin(2*np.pi*n*freq*t)/n
    return y*0.6
def bass(freq,d=0.24,a=1.0):
    t=T(d); env=np.minimum(1,t*400)*np.exp(-t*9)
    return a*(saw(freq,t,900)*0.7+np.sin(2*np.pi*freq*t))*env
def stab(freqs,d=0.5,a=1.0):
    t=T(d); y=np.zeros((len(t),2)); env=np.minimum(1,t*500)*np.exp(-t*7)
    for i,f in enumerate(freqs):
        for det,ch in ((0.997,0),(1.003,1)): y[:,ch]+=saw(f*det,t,3500)
    return a*y*env[:,None]/len(freqs)
def pluck(f,a=1.0,d=0.5):
    t=T(d); return a*(np.sin(2*np.pi*f*t)+.3*np.sin(4*np.pi*f*t))*np.exp(-t*9)
def pad(freqs,d,a=1.0):
    t=T(d); y=np.zeros((len(t),2)); env=np.minimum(1,t/0.25)*np.clip((d-t)/0.5,0,1)
    for f in freqs:
        for det,ch in ((0.995,0),(1.005,1)): y[:,ch]+=saw(f*det,t,2200)
    return a*y*env[:,None]/len(freqs)
def whoosh(d,f0,f1,a=1.0,pan0=-.8,pan1=.8,shape='bell'):
    t=T(d); u=t/d; cut=f0*(f1/f0)**u
    env=np.sin(np.pi*u)**2 if shape=='bell' else u**3
    n=lp(rng.standard_normal(len(t)),cut); n=n-lp(n,cut*0.35)
    n=n/ (np.max(np.abs(n))+1e-9)*env
    pan=pan0+(pan1-pan0)*u; l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    return a*np.stack([n*l,n*r],1)*1.4
def riser(d,f0,f1,a=1.0):
    t=T(d); u=t/d; f=f0*(f1/f0)**(u**2); ph=2*np.pi*np.cumsum(f)/SR
    tone=(np.sin(ph)+0.5*np.sin(2*ph+1)+0.3*np.sign(np.sin(ph*0.5)))*0.3
    return a*tone*u**2.5
def glitchb(d,a=1.0):
    t=T(d); n=rng.standard_normal(len(t)); n=np.repeat(n[::40],40)[:len(t)]; return a*np.round(n*3)/3*0.5
# ---- notes ----
A1,F1,C2,G1=55.0,43.65,65.41,49.0
CH={'Am':[220,261.6,329.6],'F':[174.6,220,261.6],'C':[196,261.6,329.6],'G':[196,246.9,293.7]}
# ---- arrangement ----
# 0.0 – 1.5 : open
for k in range(40): put(dry,0.08+k*0.013,tick(3200+400*(k%3),0.10,0.015),pan=0.3)
put(dry,0.05,blip(1800,700,.5)); put(wet,0.05,blip(1800,700,.25))
put(dry,0.30,blip(300,520,.35,0.2))                        # anticipation squash
put(dry,0.50,whoosh(0.4,400,6000,.6,-.9,.9))               # stretch into line
put(dry,0.70,riser(0.8,110,880,.35)); put(dry,0.7,whoosh(0.8,300,9000,.5,0,0,'up'))
put(dry,1.20,whoosh(0.42,1500,5000,.55,-.6,.9))            # bars slide off
# 1.5 impact
put(dry,1.5,kick(1.2)); put(dry,1.5,sub(0.9)); put(wet,1.5,crash(.35)); put(wet,1.5,stab(CH['Am'],0.9,.55)); put(dry,1.5,stab([110,164.8],0.6,.4))
for i in range(6): put(dry,1.45+i*0.055+0.05,kick(.18),pan=-.5+i*.2)
for b in (2.0,2.5): put(dry,b,kick(1.0))
for k in range(8): put(dry,1.5+k*0.25,hat(.25),pan=.3)
put(dry,2.0,blip(1200,300,.5,0.3)); put(wet,2.0,blip(1200,300,.3,0.3))  # the full stop
put(dry,2.5,glitchb(0.09,.45)); put(dry,2.5,clap(.6)); put(wet,2.5,clap(.3))
put(dry,2.55,whoosh(0.45,200,12000,.7,0,0,'up')); put(dry,2.55,riser(0.45,200,1600,.35))
# 3.0 – 5.0 timing
put(dry,3.0,kick(1.1)); put(dry,3.0,sub(.6,.8)); put(wet,3.0,crash(.25,1.0))
penta=[440,523.3,587.3,659.3,784,880]
for i in range(6): put(dry,3.3+i*0.07,pluck(penta[i],.35),pan=-.6+i*.24); put(wet,3.3+i*0.07,pluck(penta[i],.25))
for i,off in enumerate([1.0,1.0,1.0,1.0,1.0,1.0]): put(dry,3.3+i*0.07+off,tick(1800+i*200,.3,.04),pan=.5)
for b in np.arange(3.5,5.0,0.5): put(dry,b,kick(.9))
for k in range(16): put(dry,3.0+k*0.125,hat(.18 if k%2 else .1,0.04),pan=.35)
for k in range(8): put(dry,3.0+k*0.25,bass(A1*(2 if k%2 else 1),.22,.35))
put(dry,4.4,whoosh(0.3,3000,400,.5,.8,0))
put(dry,4.66,whoosh(0.34,150,8000,.6,0,0,'up'))
# 5.0 – 7.0 rhythm
for b in np.arange(5.0,7.0,0.5): put(dry,b,kick(1.1))
put(dry,5.0,sub(.7,.9)); put(wet,5.0,crash(.3,1.2))
for b in (5.5,6.5): put(dry,b,clap(.8)); put(wet,b,clap(.35))
for k in range(32): put(dry,5.0+k*0.0625,hat(.2 if k%4==2 else .09,0.03),pan=.4*np.sin(k))
for k in range(8): put(dry,5.0+k*0.25,bass(F1*(2 if k%2 else 1),.22,.45))
put(dry,6.72,whoosh(0.3,800,9000,.75,-.9,.9)); put(dry,6.72,glitchb(.05,.2))
# 7.0 – 9.0 form
put(dry,7.0,kick(1.1)); put(wet,7.0,stab(CH['C'],.8,.4)); put(wet,7.0,crash(.22,1.0))
for b in np.arange(7.5,9.0,0.5): put(dry,b,kick(.95))
for b in (7.5,8.5): put(dry,b,clap(.6)); put(wet,b,clap(.25))
for k in range(16): put(dry,7.0+k*0.125,hat(.15 if k%2 else .08,0.04),pan=-.3)
for k in range(8): put(dry,7.0+k*0.25,bass(C2*(2 if k%2 else 1),.22,.4))
for i,kt in enumerate([7.4,7.8,8.2,8.6]): put(dry,kt,whoosh(0.3,600,4000,.35,-.7 if i%2 else .7,.7 if i%2 else -.7))
for k in range(24): put(dry,8.8+k*0.016,tick(2600+(k%5)*300,.13,.02),pan=-1+k/12)
# 9.0 – 11.0 type
put(dry,9.0,kick(1.1)); put(dry,9.0,sub(.6,.8)); put(dry,9.0,glitchb(.07,.35)); put(wet,9.0,crash(.25,1.0))
chords=['Am','Am','F','F','C','C','G']
for k in range(7):
    put(wet,9.0+k*0.25,stab(CH[chords[k]],.35,.45)); put(dry,9.0+k*0.25,stab(CH[chords[k]],.25,.3))
for b in np.arange(9.5,11.0,0.5): put(dry,b,kick(.95))
for b in (9.5,10.5): put(dry,b,clap(.7)); put(wet,b,clap(.3))
for k in range(28): put(dry,9.0+k*0.0625,hat(.14 if k%2 else .07,0.03),pan=.3)
for k in range(7): put(dry,9.0+k*0.25,bass(G1*(2 if k%2 else 1) if k>4 else A1*(2 if k%2 else 1),.22,.4))
put(dry,10.85,whoosh(0.3,400,10000,1.0,.9,-.9))
# 11.0 – 13.0 systems
put(dry,11.0,kick(1.0)); put(wet,11.0,crash(.2,1.2))
put(dry,11.1,whoosh(1.1,200,2500,.45,-.6,.6))
put(dry,11.3,riser(0.95,90,700,.35))
put(dry,11.5,whoosh(0.72,500,14000,.55,0,0,'up'))          # reverse cymbal
for k in range(8): put(dry,11.25+k*0.125,kick(.25+.08*k))  # build
put(dry,12.25,kick(1.3)); put(dry,12.25,sub(1.0,1.2)); put(wet,12.25,crash(.45,1.8)); put(wet,12.25,stab(CH['Am'],1.0,.6)); put(dry,12.25,glitchb(.1,.4))
put(dry,12.6,riser(0.4,80,2400,.4)); put(dry,12.6,whoosh(0.4,300,9000,.6,.8,-.8,'up'))
# 13.0 – 15.0 end
put(dry,13.0,kick(1.2)); put(dry,13.0,sub(1.0,1.8)); put(wet,13.0,crash(.3,2.0))
put(wet,13.0,pad([110,220,261.6,329.6,392,493.9],1.85,.55))
for i in range(6): put(dry,13.3+i*0.045+0.06,tick(1500+i*150,.25,.04),pan=-.5+i*.2)
for i in range(12): put(dry,13.55+i*0.046,tick(4200,.08,.012),pan=.4)
for k in range(30): put(dry,13.9+k*0.017,tick(3000+300*(k%3),.07,.012),pan=-.2)
put(dry,14.72,whoosh(0.26,3000,300,.5,0,0))
put(dry,14.97,kick(.8)); put(dry,14.97,tick(900,.4,.03))
# ---- mix ----
L=int(1.4*SR); t=np.arange(L)/SR
ir=np.stack([rng.standard_normal(L)*np.exp(-t*4.2),rng.standard_normal(L)*np.exp(-t*4.4)],1); ir[:int(.012*SR)]=0
M=1<<int(np.ceil(np.log2(N+L)))
rev=np.stack([np.fft.irfft(np.fft.rfft(wet[:,c],M)*np.fft.rfft(ir[:,c],M),M)[:N] for c in range(2)],1)
rev/=np.max(np.abs(rev))+1e-9
mix=dry+wet*0.6+rev*0.22
fade=np.ones(N); fe=int(14.99*SR); fade[fe:]=0
mix*=fade[:,None]
mix=np.tanh(mix*0.9)
mix/=np.max(np.abs(mix)); mix*=10**(-1/20)
pcm=(mix*32767).astype('<i2')
with wave.open('reel.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok', mix.shape)
