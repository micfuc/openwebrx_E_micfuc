OpenWebRX
=========

OpenWebRX is a multi-user SDR receiver software with a web interface. 

It has the following features:

- [csdr](https://github.com/jketterl/csdr) based demodulators (AM/FM/SSB/CW/BPSK31/BPSK63)
- filter passband can be set from GUI
- it extensively uses HTML5 features like WebSocket, Web Audio API, and Canvas
- it works in Google Chrome, Chromium and Mozilla Firefox
- supports a wide range of [SDR hardware](https://github.com/jketterl/openwebrx/wiki/Supported-Hardware#sdr-devices)
- Multiple SDR devices can be used simultaneously
- [digiham](https://github.com/jketterl/digiham) based demodularors (DMR, YSF, Pocsag, D-Star, NXDN)
- [wsjt-x](https://physics.princeton.edu/pulsar/k1jt/wsjtx.html) based demodulators (FT8, FT4, WSPR, JT65, JT9, FST4,
  FST4W)
- [direwolf](https://github.com/wb2osz/direwolf) based demodulation of APRS packets
- [JS8Call](http://js8call.com/) support
- [DRM](https://github.com/jketterl/openwebrx/wiki/DRM-demodulator-notes) support
- [FreeDV](https://github.com/jketterl/openwebrx/wiki/FreeDV-demodulator-notes) support
- M17 support based on [m17-cxx-demod](https://github.com/mobilinkd/m17-cxx-demod)

## Setup

The following methods of setting up this 'E' version of OpenwebRX are available:

- Manual installation

Jakob Ketterl has gone to some trouble to make it easy to install his build, including productions of pre-built packages and docker images. Please see the [setup guide on Jakob's wiki](https://github.com/jketterl/openwebrx/wiki/Setup-Guide) for more details on these other methods.

## Information

[Jakob Ketterl](https://github.com/jketterl/) has done a *lot* of work improving OpenWebRX which was orignally created by [András Retzler](https://github.com/ha7ilm). Jakob has formed a group list on:

[our groups.io group](https://groups.io/g/openwebrx).

Jakob has a wealth of knowledge and is usually responsive on his group. This fork is absolutely not intended
to supercede his work, which should be seen as the primary source for all things good on OWRX. 

What will appear here is a somewhat experimental version of OpenWebRX, which I have dubbed the 'E' version. It will contain changes that have been implemented following personal request(s), and in the interests of possibly enhancing this great software I make these public. Hopefully the contributions will be useful to some, and if you've something to contribute back I'd be pleased to hear from you. 

Any changes you see here should be considered alpha. I only test with Firefox and, other than myself, there is just one other person
that uses my installation very occasionally. Thus it's quite possible bugs may arise from what I've done - so please bear this in mind 
if you trial anything, best make a backup beforehand!

Recent changes include:

*  Addition of frequency change buttons, allowing the use of click-change to frequency
*  Addition of stepchange button for change from 5kHz to 9kHz steps for broadcast SWL
*  Addition of Spectrum display - this is somewhat new and may well get some changes 
*  Alteration/addition to allow for slower AGC in SSB operation (may need addition to pycsdr)
*  Addition of 'ghost' mode - makes much of the receiver panel transparent so the waterfall is visible behind
*  Add smeter scale, decouple smeter from waterfall (now gets value direct from csdr), add js meter for performance benefits

## Licensing

OpenWebRX is available under Affero GPL v3 license
([summary](https://tldrlegal.com/license/gnu-affero-general-public-license-v3-(agpl-3.0))).

OpenWebRX is also available under a commercial license on request. Please contact Andras at the address
*&lt;randras@sdr.hu&gt;* for licensing options. 
