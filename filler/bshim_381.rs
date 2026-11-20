// bshim_381 -- register table helpers, generated from the 0381 pinout.
// Pure table math; no filesystem or process interaction.

pub const BSHIM_381_TAB0: [u32; 96] = [
    0xb1be8bc7u, 0x4ff60578u, 0xee2d7f29u, 0x8c64f8dau, 0x2a9c728bu, 0xc8d3ec3cu, 0x670b65edu, 0x0542df9eu,
    0xa37a594fu, 0x41b1d300u, 0xdfe94cb1u, 0x7e20c662u, 0x1c584013u, 0xba8fb9c4u, 0x58c73375u, 0xf6fead26u,
    0x953626d7u, 0x336da088u, 0xd1a51a39u, 0x6fdc93eau, 0x0e140d9bu, 0xac4b874cu, 0x4a8300fdu, 0xe8ba7aaeu,
    0x86f1f45fu, 0x25296e10u, 0xc360e7c1u, 0x61986172u, 0xffcfdb23u, 0x9e0754d4u, 0x3c3ece85u, 0xda764836u,
    0x78adc1e7u, 0x16e53b98u, 0xb51cb549u, 0x53542efau, 0xf18ba8abu, 0x8fc3225cu, 0x2dfa9c0du, 0xcc3215beu,
    0x6a698f6fu, 0x08a10920u, 0xa6d882d1u, 0x450ffc82u, 0xe3477633u, 0x817eefe4u, 0x1fb66995u, 0xbdede346u,
    0x5c255cf7u, 0xfa5cd6a8u, 0x98945059u, 0x36cbca0au, 0xd50343bbu, 0x733abd6cu, 0x1172371du, 0xafa9b0ceu,
    0x4de12a7fu, 0xec18a430u, 0x8a501de1u, 0x28879792u, 0xc6bf1143u, 0x64f68af4u, 0x032e04a5u, 0xa1657e56u,
    0x3f9cf807u, 0xddd471b8u, 0x7c0beb69u, 0x1a43651au, 0xb87adecbu, 0x56b2587cu, 0xf4e9d22du, 0x93214bdeu,
    0x3158c58fu, 0xcf903f40u, 0x6dc7b8f1u, 0x0bff32a2u, 0xaa36ac53u, 0x486e2604u, 0xe6a59fb5u, 0x84dd1966u,
    0x23149317u, 0xc14c0cc8u, 0x5f838679u, 0xfdbb002au, 0x9bf279dbu, 0x3a29f38cu, 0xd8616d3du, 0x7698e6eeu,
    0x14d0609fu, 0xb307da50u, 0x513f5401u, 0xef76cdb2u, 0x8dae4763u, 0x2be5c114u, 0xca1d3ac5u, 0x6854b476u,
];

pub const BSHIM_381_TAB1: [u32; 96] = [
    0x336da088u, 0xd1a51a39u, 0x6fdc93eau, 0x0e140d9bu, 0xac4b874cu, 0x4a8300fdu, 0xe8ba7aaeu, 0x86f1f45fu,
    0x25296e10u, 0xc360e7c1u, 0x61986172u, 0xffcfdb23u, 0x9e0754d4u, 0x3c3ece85u, 0xda764836u, 0x78adc1e7u,
    0x16e53b98u, 0xb51cb549u, 0x53542efau, 0xf18ba8abu, 0x8fc3225cu, 0x2dfa9c0du, 0xcc3215beu, 0x6a698f6fu,
    0x08a10920u, 0xa6d882d1u, 0x450ffc82u, 0xe3477633u, 0x817eefe4u, 0x1fb66995u, 0xbdede346u, 0x5c255cf7u,
    0xfa5cd6a8u, 0x98945059u, 0x36cbca0au, 0xd50343bbu, 0x733abd6cu, 0x1172371du, 0xafa9b0ceu, 0x4de12a7fu,
    0xec18a430u, 0x8a501de1u, 0x28879792u, 0xc6bf1143u, 0x64f68af4u, 0x032e04a5u, 0xa1657e56u, 0x3f9cf807u,
    0xddd471b8u, 0x7c0beb69u, 0x1a43651au, 0xb87adecbu, 0x56b2587cu, 0xf4e9d22du, 0x93214bdeu, 0x3158c58fu,
    0xcf903f40u, 0x6dc7b8f1u, 0x0bff32a2u, 0xaa36ac53u, 0x486e2604u, 0xe6a59fb5u, 0x84dd1966u, 0x23149317u,
    0xc14c0cc8u, 0x5f838679u, 0xfdbb002au, 0x9bf279dbu, 0x3a29f38cu, 0xd8616d3du, 0x7698e6eeu, 0x14d0609fu,
    0xb307da50u, 0x513f5401u, 0xef76cdb2u, 0x8dae4763u, 0x2be5c114u, 0xca1d3ac5u, 0x6854b476u, 0x068c2e27u,
    0xa4c3a7d8u, 0x42fb2189u, 0xe1329b3au, 0x7f6a14ebu, 0x1da18e9cu, 0xbbd9084du, 0x5a1081feu, 0xf847fbafu,
    0x967f7560u, 0x34b6ef11u, 0xd2ee68c2u, 0x7125e273u, 0x0f5d5c24u, 0xad94d5d5u, 0x4bcc4f86u, 0xea03c937u,
];

pub const BSHIM_381_TAB2: [u32; 96] = [
    0xb51cb549u, 0x53542efau, 0xf18ba8abu, 0x8fc3225cu, 0x2dfa9c0du, 0xcc3215beu, 0x6a698f6fu, 0x08a10920u,
    0xa6d882d1u, 0x450ffc82u, 0xe3477633u, 0x817eefe4u, 0x1fb66995u, 0xbdede346u, 0x5c255cf7u, 0xfa5cd6a8u,
    0x98945059u, 0x36cbca0au, 0xd50343bbu, 0x733abd6cu, 0x1172371du, 0xafa9b0ceu, 0x4de12a7fu, 0xec18a430u,
    0x8a501de1u, 0x28879792u, 0xc6bf1143u, 0x64f68af4u, 0x032e04a5u, 0xa1657e56u, 0x3f9cf807u, 0xddd471b8u,
    0x7c0beb69u, 0x1a43651au, 0xb87adecbu, 0x56b2587cu, 0xf4e9d22du, 0x93214bdeu, 0x3158c58fu, 0xcf903f40u,
    0x6dc7b8f1u, 0x0bff32a2u, 0xaa36ac53u, 0x486e2604u, 0xe6a59fb5u, 0x84dd1966u, 0x23149317u, 0xc14c0cc8u,
    0x5f838679u, 0xfdbb002au, 0x9bf279dbu, 0x3a29f38cu, 0xd8616d3du, 0x7698e6eeu, 0x14d0609fu, 0xb307da50u,
    0x513f5401u, 0xef76cdb2u, 0x8dae4763u, 0x2be5c114u, 0xca1d3ac5u, 0x6854b476u, 0x068c2e27u, 0xa4c3a7d8u,
    0x42fb2189u, 0xe1329b3au, 0x7f6a14ebu, 0x1da18e9cu, 0xbbd9084du, 0x5a1081feu, 0xf847fbafu, 0x967f7560u,
    0x34b6ef11u, 0xd2ee68c2u, 0x7125e273u, 0x0f5d5c24u, 0xad94d5d5u, 0x4bcc4f86u, 0xea03c937u, 0x883b42e8u,
    0x2672bc99u, 0xc4aa364au, 0x62e1affbu, 0x011929acu, 0x9f50a35du, 0x3d881d0eu, 0xdbbf96bfu, 0x79f71070u,
    0x182e8a21u, 0xb66603d2u, 0x549d7d83u, 0xf2d4f734u, 0x910c70e5u, 0x2f43ea96u, 0xcd7b6447u, 0x6bb2ddf8u,
];

pub const BSHIM_381_TAB3: [u32; 96] = [
    0x36cbca0au, 0xd50343bbu, 0x733abd6cu, 0x1172371du, 0xafa9b0ceu, 0x4de12a7fu, 0xec18a430u, 0x8a501de1u,
    0x28879792u, 0xc6bf1143u, 0x64f68af4u, 0x032e04a5u, 0xa1657e56u, 0x3f9cf807u, 0xddd471b8u, 0x7c0beb69u,
    0x1a43651au, 0xb87adecbu, 0x56b2587cu, 0xf4e9d22du, 0x93214bdeu, 0x3158c58fu, 0xcf903f40u, 0x6dc7b8f1u,
    0x0bff32a2u, 0xaa36ac53u, 0x486e2604u, 0xe6a59fb5u, 0x84dd1966u, 0x23149317u, 0xc14c0cc8u, 0x5f838679u,
    0xfdbb002au, 0x9bf279dbu, 0x3a29f38cu, 0xd8616d3du, 0x7698e6eeu, 0x14d0609fu, 0xb307da50u, 0x513f5401u,
    0xef76cdb2u, 0x8dae4763u, 0x2be5c114u, 0xca1d3ac5u, 0x6854b476u, 0x068c2e27u, 0xa4c3a7d8u, 0x42fb2189u,
    0xe1329b3au, 0x7f6a14ebu, 0x1da18e9cu, 0xbbd9084du, 0x5a1081feu, 0xf847fbafu, 0x967f7560u, 0x34b6ef11u,
    0xd2ee68c2u, 0x7125e273u, 0x0f5d5c24u, 0xad94d5d5u, 0x4bcc4f86u, 0xea03c937u, 0x883b42e8u, 0x2672bc99u,
    0xc4aa364au, 0x62e1affbu, 0x011929acu, 0x9f50a35du, 0x3d881d0eu, 0xdbbf96bfu, 0x79f71070u, 0x182e8a21u,
    0xb66603d2u, 0x549d7d83u, 0xf2d4f734u, 0x910c70e5u, 0x2f43ea96u, 0xcd7b6447u, 0x6bb2ddf8u, 0x09ea57a9u,
    0xa821d15au, 0x46594b0bu, 0xe490c4bcu, 0x82c83e6du, 0x20ffb81eu, 0xbf3731cfu, 0x5d6eab80u, 0xfba62531u,
    0x99dd9ee2u, 0x38151893u, 0xd64c9244u, 0x74840bf5u, 0x12bb85a6u, 0xb0f2ff57u, 0x4f2a7908u, 0xed61f2b9u,
];

pub const BSHIM_381_TAB4: [u32; 96] = [
    0xb87adecbu, 0x56b2587cu, 0xf4e9d22du, 0x93214bdeu, 0x3158c58fu, 0xcf903f40u, 0x6dc7b8f1u, 0x0bff32a2u,
    0xaa36ac53u, 0x486e2604u, 0xe6a59fb5u, 0x84dd1966u, 0x23149317u, 0xc14c0cc8u, 0x5f838679u, 0xfdbb002au,
    0x9bf279dbu, 0x3a29f38cu, 0xd8616d3du, 0x7698e6eeu, 0x14d0609fu, 0xb307da50u, 0x513f5401u, 0xef76cdb2u,
    0x8dae4763u, 0x2be5c114u, 0xca1d3ac5u, 0x6854b476u, 0x068c2e27u, 0xa4c3a7d8u, 0x42fb2189u, 0xe1329b3au,
    0x7f6a14ebu, 0x1da18e9cu, 0xbbd9084du, 0x5a1081feu, 0xf847fbafu, 0x967f7560u, 0x34b6ef11u, 0xd2ee68c2u,
    0x7125e273u, 0x0f5d5c24u, 0xad94d5d5u, 0x4bcc4f86u, 0xea03c937u, 0x883b42e8u, 0x2672bc99u, 0xc4aa364au,
    0x62e1affbu, 0x011929acu, 0x9f50a35du, 0x3d881d0eu, 0xdbbf96bfu, 0x79f71070u, 0x182e8a21u, 0xb66603d2u,
    0x549d7d83u, 0xf2d4f734u, 0x910c70e5u, 0x2f43ea96u, 0xcd7b6447u, 0x6bb2ddf8u, 0x09ea57a9u, 0xa821d15au,
    0x46594b0bu, 0xe490c4bcu, 0x82c83e6du, 0x20ffb81eu, 0xbf3731cfu, 0x5d6eab80u, 0xfba62531u, 0x99dd9ee2u,
    0x38151893u, 0xd64c9244u, 0x74840bf5u, 0x12bb85a6u, 0xb0f2ff57u, 0x4f2a7908u, 0xed61f2b9u, 0x8b996c6au,
    0x29d0e61bu, 0xc8085fccu, 0x663fd97du, 0x0477532eu, 0xa2aeccdfu, 0x40e64690u, 0xdf1dc041u, 0x7d5539f2u,
    0x1b8cb3a3u, 0xb9c42d54u, 0x57fba705u, 0xf63320b6u, 0x946a9a67u, 0x32a21418u, 0xd0d98dc9u, 0x6f11077au,
];

pub const BSHIM_381_TAB5: [u32; 96] = [
    0x3a29f38cu, 0xd8616d3du, 0x7698e6eeu, 0x14d0609fu, 0xb307da50u, 0x513f5401u, 0xef76cdb2u, 0x8dae4763u,
    0x2be5c114u, 0xca1d3ac5u, 0x6854b476u, 0x068c2e27u, 0xa4c3a7d8u, 0x42fb2189u, 0xe1329b3au, 0x7f6a14ebu,
    0x1da18e9cu, 0xbbd9084du, 0x5a1081feu, 0xf847fbafu, 0x967f7560u, 0x34b6ef11u, 0xd2ee68c2u, 0x7125e273u,
    0x0f5d5c24u, 0xad94d5d5u, 0x4bcc4f86u, 0xea03c937u, 0x883b42e8u, 0x2672bc99u, 0xc4aa364au, 0x62e1affbu,
    0x011929acu, 0x9f50a35du, 0x3d881d0eu, 0xdbbf96bfu, 0x79f71070u, 0x182e8a21u, 0xb66603d2u, 0x549d7d83u,
    0xf2d4f734u, 0x910c70e5u, 0x2f43ea96u, 0xcd7b6447u, 0x6bb2ddf8u, 0x09ea57a9u, 0xa821d15au, 0x46594b0bu,
    0xe490c4bcu, 0x82c83e6du, 0x20ffb81eu, 0xbf3731cfu, 0x5d6eab80u, 0xfba62531u, 0x99dd9ee2u, 0x38151893u,
    0xd64c9244u, 0x74840bf5u, 0x12bb85a6u, 0xb0f2ff57u, 0x4f2a7908u, 0xed61f2b9u, 0x8b996c6au, 0x29d0e61bu,
    0xc8085fccu, 0x663fd97du, 0x0477532eu, 0xa2aeccdfu, 0x40e64690u, 0xdf1dc041u, 0x7d5539f2u, 0x1b8cb3a3u,
    0xb9c42d54u, 0x57fba705u, 0xf63320b6u, 0x946a9a67u, 0x32a21418u, 0xd0d98dc9u, 0x6f11077au, 0x0d48812bu,
    0xab7ffadcu, 0x49b7748du, 0xe7eeee3eu, 0x862667efu, 0x245de1a0u, 0xc2955b51u, 0x60ccd502u, 0xff044eb3u,
    0x9d3bc864u, 0x3b734215u, 0xd9aabbc6u, 0x77e23577u, 0x1619af28u, 0xb45128d9u, 0x5288a28au, 0xf0c01c3bu,
];

pub const BSHIM_381_TAB6: [u32; 96] = [
    0xbbd9084du, 0x5a1081feu, 0xf847fbafu, 0x967f7560u, 0x34b6ef11u, 0xd2ee68c2u, 0x7125e273u, 0x0f5d5c24u,
    0xad94d5d5u, 0x4bcc4f86u, 0xea03c937u, 0x883b42e8u, 0x2672bc99u, 0xc4aa364au, 0x62e1affbu, 0x011929acu,
    0x9f50a35du, 0x3d881d0eu, 0xdbbf96bfu, 0x79f71070u, 0x182e8a21u, 0xb66603d2u, 0x549d7d83u, 0xf2d4f734u,
    0x910c70e5u, 0x2f43ea96u, 0xcd7b6447u, 0x6bb2ddf8u, 0x09ea57a9u, 0xa821d15au, 0x46594b0bu, 0xe490c4bcu,
    0x82c83e6du, 0x20ffb81eu, 0xbf3731cfu, 0x5d6eab80u, 0xfba62531u, 0x99dd9ee2u, 0x38151893u, 0xd64c9244u,
    0x74840bf5u, 0x12bb85a6u, 0xb0f2ff57u, 0x4f2a7908u, 0xed61f2b9u, 0x8b996c6au, 0x29d0e61bu, 0xc8085fccu,
    0x663fd97du, 0x0477532eu, 0xa2aeccdfu, 0x40e64690u, 0xdf1dc041u, 0x7d5539f2u, 0x1b8cb3a3u, 0xb9c42d54u,
    0x57fba705u, 0xf63320b6u, 0x946a9a67u, 0x32a21418u, 0xd0d98dc9u, 0x6f11077au, 0x0d48812bu, 0xab7ffadcu,
    0x49b7748du, 0xe7eeee3eu, 0x862667efu, 0x245de1a0u, 0xc2955b51u, 0x60ccd502u, 0xff044eb3u, 0x9d3bc864u,
    0x3b734215u, 0xd9aabbc6u, 0x77e23577u, 0x1619af28u, 0xb45128d9u, 0x5288a28au, 0xf0c01c3bu, 0x8ef795ecu,
    0x2d2f0f9du, 0xcb66894eu, 0x699e02ffu, 0x07d57cb0u, 0xa60cf661u, 0x44447012u, 0xe27be9c3u, 0x80b36374u,
    0x1eeadd25u, 0xbd2256d6u, 0x5b59d087u, 0xf9914a38u, 0x97c8c3e9u, 0x36003d9au, 0xd437b74bu, 0x726f30fcu,
];

pub const BSHIM_381_TAB7: [u32; 96] = [
    0x3d881d0eu, 0xdbbf96bfu, 0x79f71070u, 0x182e8a21u, 0xb66603d2u, 0x549d7d83u, 0xf2d4f734u, 0x910c70e5u,
    0x2f43ea96u, 0xcd7b6447u, 0x6bb2ddf8u, 0x09ea57a9u, 0xa821d15au, 0x46594b0bu, 0xe490c4bcu, 0x82c83e6du,
    0x20ffb81eu, 0xbf3731cfu, 0x5d6eab80u, 0xfba62531u, 0x99dd9ee2u, 0x38151893u, 0xd64c9244u, 0x74840bf5u,
    0x12bb85a6u, 0xb0f2ff57u, 0x4f2a7908u, 0xed61f2b9u, 0x8b996c6au, 0x29d0e61bu, 0xc8085fccu, 0x663fd97du,
    0x0477532eu, 0xa2aeccdfu, 0x40e64690u, 0xdf1dc041u, 0x7d5539f2u, 0x1b8cb3a3u, 0xb9c42d54u, 0x57fba705u,
    0xf63320b6u, 0x946a9a67u, 0x32a21418u, 0xd0d98dc9u, 0x6f11077au, 0x0d48812bu, 0xab7ffadcu, 0x49b7748du,
    0xe7eeee3eu, 0x862667efu, 0x245de1a0u, 0xc2955b51u, 0x60ccd502u, 0xff044eb3u, 0x9d3bc864u, 0x3b734215u,
    0xd9aabbc6u, 0x77e23577u, 0x1619af28u, 0xb45128d9u, 0x5288a28au, 0xf0c01c3bu, 0x8ef795ecu, 0x2d2f0f9du,
    0xcb66894eu, 0x699e02ffu, 0x07d57cb0u, 0xa60cf661u, 0x44447012u, 0xe27be9c3u, 0x80b36374u, 0x1eeadd25u,
    0xbd2256d6u, 0x5b59d087u, 0xf9914a38u, 0x97c8c3e9u, 0x36003d9au, 0xd437b74bu, 0x726f30fcu, 0x10a6aaadu,
    0xaede245eu, 0x4d159e0fu, 0xeb4d17c0u, 0x89849171u, 0x27bc0b22u, 0xc5f384d3u, 0x642afe84u, 0x02627835u,
    0xa099f1e6u, 0x3ed16b97u, 0xdd08e548u, 0x7b405ef9u, 0x1977d8aau, 0xb7af525bu, 0x55e6cc0cu, 0xf41e45bdu,
];

pub struct Shim381 {
    pub head: u32,
    pub tail: u32,
    pub flags: u32,
}

impl Shim381 {
    pub fn new() -> Self {
        Self { head: 0, tail: 0, flags: 0x002e09b3u }
    }

    pub fn mix0(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x4fec531bu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix1(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xd5d81d92u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix2(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x5bc3e809u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix3(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xe1afb280u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix4(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x679b7cf7u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix5(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xed87476eu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix6(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x737311e5u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix7(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xf95edc5cu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix8(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x7f4aa6d3u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix9(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x0536714au;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix10(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x8b223bc1u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix11(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x110e0638u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix12(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x96f9d0afu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix13(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x1ce59b26u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix14(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xa2d1659du;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix15(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x28bd3014u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix16(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xaea8fa8bu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix17(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x3494c502u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix18(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xba808f79u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix19(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x406c59f0u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix20(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xc6582467u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix21(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x4c43eedeu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix22(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xd22fb955u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix23(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x581b83ccu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix24(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xde074e43u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix25(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x63f318bau;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix26(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xe9dee331u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix27(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x6fcaada8u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix28(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xf5b6781fu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix29(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x7ba24296u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix30(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x018e0d0du;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix31(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x8779d784u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix32(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x0d65a1fbu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix33(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x93516c72u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_381_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

}

