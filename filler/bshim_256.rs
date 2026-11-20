// bshim_256 -- register table helpers, generated from the 0256 pinout.
// Pure table math; no filesystem or process interaction.

pub const BSHIM_256_TAB0: [u32; 96] = [
    0x63459300u, 0x017d0cb1u, 0x9fb48662u, 0x3dec0013u, 0xdc2379c4u, 0x7a5af375u, 0x18926d26u, 0xb6c9e6d7u,
    0x55016088u, 0xf338da39u, 0x917053eau, 0x2fa7cd9bu, 0xcddf474cu, 0x6c16c0fdu, 0x0a4e3aaeu, 0xa885b45fu,
    0x46bd2e10u, 0xe4f4a7c1u, 0x832c2172u, 0x21639b23u, 0xbf9b14d4u, 0x5dd28e85u, 0xfc0a0836u, 0x9a4181e7u,
    0x3878fb98u, 0xd6b07549u, 0x74e7eefau, 0x131f68abu, 0xb156e25cu, 0x4f8e5c0du, 0xedc5d5beu, 0x8bfd4f6fu,
    0x2a34c920u, 0xc86c42d1u, 0x66a3bc82u, 0x04db3633u, 0xa312afe4u, 0x414a2995u, 0xdf81a346u, 0x7db91cf7u,
    0x1bf096a8u, 0xba281059u, 0x585f8a0au, 0xf69703bbu, 0x94ce7d6cu, 0x3305f71du, 0xd13d70ceu, 0x6f74ea7fu,
    0x0dac6430u, 0xabe3dde1u, 0x4a1b5792u, 0xe852d143u, 0x868a4af4u, 0x24c1c4a5u, 0xc2f93e56u, 0x6130b807u,
    0xff6831b8u, 0x9d9fab69u, 0x3bd7251au, 0xda0e9ecbu, 0x7846187cu, 0x167d922du, 0xb4b50bdeu, 0x52ec858fu,
    0xf123ff40u, 0x8f5b78f1u, 0x2d92f2a2u, 0xcbca6c53u, 0x6a01e604u, 0x08395fb5u, 0xa670d966u, 0x44a85317u,
    0xe2dfccc8u, 0x81174679u, 0x1f4ec02au, 0xbd8639dbu, 0x5bbdb38cu, 0xf9f52d3du, 0x982ca6eeu, 0x3664209fu,
    0xd49b9a50u, 0x72d31401u, 0x110a8db2u, 0xaf420763u, 0x4d798114u, 0xebb0fac5u, 0x89e87476u, 0x281fee27u,
    0xc65767d8u, 0x648ee189u, 0x02c65b3au, 0xa0fdd4ebu, 0x3f354e9cu, 0xdd6cc84du, 0x7ba441feu, 0x19dbbbafu,
];

pub const BSHIM_256_TAB1: [u32; 96] = [
    0xe4f4a7c1u, 0x832c2172u, 0x21639b23u, 0xbf9b14d4u, 0x5dd28e85u, 0xfc0a0836u, 0x9a4181e7u, 0x3878fb98u,
    0xd6b07549u, 0x74e7eefau, 0x131f68abu, 0xb156e25cu, 0x4f8e5c0du, 0xedc5d5beu, 0x8bfd4f6fu, 0x2a34c920u,
    0xc86c42d1u, 0x66a3bc82u, 0x04db3633u, 0xa312afe4u, 0x414a2995u, 0xdf81a346u, 0x7db91cf7u, 0x1bf096a8u,
    0xba281059u, 0x585f8a0au, 0xf69703bbu, 0x94ce7d6cu, 0x3305f71du, 0xd13d70ceu, 0x6f74ea7fu, 0x0dac6430u,
    0xabe3dde1u, 0x4a1b5792u, 0xe852d143u, 0x868a4af4u, 0x24c1c4a5u, 0xc2f93e56u, 0x6130b807u, 0xff6831b8u,
    0x9d9fab69u, 0x3bd7251au, 0xda0e9ecbu, 0x7846187cu, 0x167d922du, 0xb4b50bdeu, 0x52ec858fu, 0xf123ff40u,
    0x8f5b78f1u, 0x2d92f2a2u, 0xcbca6c53u, 0x6a01e604u, 0x08395fb5u, 0xa670d966u, 0x44a85317u, 0xe2dfccc8u,
    0x81174679u, 0x1f4ec02au, 0xbd8639dbu, 0x5bbdb38cu, 0xf9f52d3du, 0x982ca6eeu, 0x3664209fu, 0xd49b9a50u,
    0x72d31401u, 0x110a8db2u, 0xaf420763u, 0x4d798114u, 0xebb0fac5u, 0x89e87476u, 0x281fee27u, 0xc65767d8u,
    0x648ee189u, 0x02c65b3au, 0xa0fdd4ebu, 0x3f354e9cu, 0xdd6cc84du, 0x7ba441feu, 0x19dbbbafu, 0xb8133560u,
    0x564aaf11u, 0xf48228c2u, 0x92b9a273u, 0x30f11c24u, 0xcf2895d5u, 0x6d600f86u, 0x0b978937u, 0xa9cf02e8u,
    0x48067c99u, 0xe63df64au, 0x84756ffbu, 0x22ace9acu, 0xc0e4635du, 0x5f1bdd0eu, 0xfd5356bfu, 0x9b8ad070u,
];

pub const BSHIM_256_TAB2: [u32; 96] = [
    0x66a3bc82u, 0x04db3633u, 0xa312afe4u, 0x414a2995u, 0xdf81a346u, 0x7db91cf7u, 0x1bf096a8u, 0xba281059u,
    0x585f8a0au, 0xf69703bbu, 0x94ce7d6cu, 0x3305f71du, 0xd13d70ceu, 0x6f74ea7fu, 0x0dac6430u, 0xabe3dde1u,
    0x4a1b5792u, 0xe852d143u, 0x868a4af4u, 0x24c1c4a5u, 0xc2f93e56u, 0x6130b807u, 0xff6831b8u, 0x9d9fab69u,
    0x3bd7251au, 0xda0e9ecbu, 0x7846187cu, 0x167d922du, 0xb4b50bdeu, 0x52ec858fu, 0xf123ff40u, 0x8f5b78f1u,
    0x2d92f2a2u, 0xcbca6c53u, 0x6a01e604u, 0x08395fb5u, 0xa670d966u, 0x44a85317u, 0xe2dfccc8u, 0x81174679u,
    0x1f4ec02au, 0xbd8639dbu, 0x5bbdb38cu, 0xf9f52d3du, 0x982ca6eeu, 0x3664209fu, 0xd49b9a50u, 0x72d31401u,
    0x110a8db2u, 0xaf420763u, 0x4d798114u, 0xebb0fac5u, 0x89e87476u, 0x281fee27u, 0xc65767d8u, 0x648ee189u,
    0x02c65b3au, 0xa0fdd4ebu, 0x3f354e9cu, 0xdd6cc84du, 0x7ba441feu, 0x19dbbbafu, 0xb8133560u, 0x564aaf11u,
    0xf48228c2u, 0x92b9a273u, 0x30f11c24u, 0xcf2895d5u, 0x6d600f86u, 0x0b978937u, 0xa9cf02e8u, 0x48067c99u,
    0xe63df64au, 0x84756ffbu, 0x22ace9acu, 0xc0e4635du, 0x5f1bdd0eu, 0xfd5356bfu, 0x9b8ad070u, 0x39c24a21u,
    0xd7f9c3d2u, 0x76313d83u, 0x1468b734u, 0xb2a030e5u, 0x50d7aa96u, 0xef0f2447u, 0x8d469df8u, 0x2b7e17a9u,
    0xc9b5915au, 0x67ed0b0bu, 0x062484bcu, 0xa45bfe6du, 0x4293781eu, 0xe0caf1cfu, 0x7f026b80u, 0x1d39e531u,
];

pub const BSHIM_256_TAB3: [u32; 96] = [
    0xe852d143u, 0x868a4af4u, 0x24c1c4a5u, 0xc2f93e56u, 0x6130b807u, 0xff6831b8u, 0x9d9fab69u, 0x3bd7251au,
    0xda0e9ecbu, 0x7846187cu, 0x167d922du, 0xb4b50bdeu, 0x52ec858fu, 0xf123ff40u, 0x8f5b78f1u, 0x2d92f2a2u,
    0xcbca6c53u, 0x6a01e604u, 0x08395fb5u, 0xa670d966u, 0x44a85317u, 0xe2dfccc8u, 0x81174679u, 0x1f4ec02au,
    0xbd8639dbu, 0x5bbdb38cu, 0xf9f52d3du, 0x982ca6eeu, 0x3664209fu, 0xd49b9a50u, 0x72d31401u, 0x110a8db2u,
    0xaf420763u, 0x4d798114u, 0xebb0fac5u, 0x89e87476u, 0x281fee27u, 0xc65767d8u, 0x648ee189u, 0x02c65b3au,
    0xa0fdd4ebu, 0x3f354e9cu, 0xdd6cc84du, 0x7ba441feu, 0x19dbbbafu, 0xb8133560u, 0x564aaf11u, 0xf48228c2u,
    0x92b9a273u, 0x30f11c24u, 0xcf2895d5u, 0x6d600f86u, 0x0b978937u, 0xa9cf02e8u, 0x48067c99u, 0xe63df64au,
    0x84756ffbu, 0x22ace9acu, 0xc0e4635du, 0x5f1bdd0eu, 0xfd5356bfu, 0x9b8ad070u, 0x39c24a21u, 0xd7f9c3d2u,
    0x76313d83u, 0x1468b734u, 0xb2a030e5u, 0x50d7aa96u, 0xef0f2447u, 0x8d469df8u, 0x2b7e17a9u, 0xc9b5915au,
    0x67ed0b0bu, 0x062484bcu, 0xa45bfe6du, 0x4293781eu, 0xe0caf1cfu, 0x7f026b80u, 0x1d39e531u, 0xbb715ee2u,
    0x59a8d893u, 0xf7e05244u, 0x9617cbf5u, 0x344f45a6u, 0xd286bf57u, 0x70be3908u, 0x0ef5b2b9u, 0xad2d2c6au,
    0x4b64a61bu, 0xe99c1fccu, 0x87d3997du, 0x260b132eu, 0xc4428cdfu, 0x627a0690u, 0x00b18041u, 0x9ee8f9f2u,
];

pub const BSHIM_256_TAB4: [u32; 96] = [
    0x6a01e604u, 0x08395fb5u, 0xa670d966u, 0x44a85317u, 0xe2dfccc8u, 0x81174679u, 0x1f4ec02au, 0xbd8639dbu,
    0x5bbdb38cu, 0xf9f52d3du, 0x982ca6eeu, 0x3664209fu, 0xd49b9a50u, 0x72d31401u, 0x110a8db2u, 0xaf420763u,
    0x4d798114u, 0xebb0fac5u, 0x89e87476u, 0x281fee27u, 0xc65767d8u, 0x648ee189u, 0x02c65b3au, 0xa0fdd4ebu,
    0x3f354e9cu, 0xdd6cc84du, 0x7ba441feu, 0x19dbbbafu, 0xb8133560u, 0x564aaf11u, 0xf48228c2u, 0x92b9a273u,
    0x30f11c24u, 0xcf2895d5u, 0x6d600f86u, 0x0b978937u, 0xa9cf02e8u, 0x48067c99u, 0xe63df64au, 0x84756ffbu,
    0x22ace9acu, 0xc0e4635du, 0x5f1bdd0eu, 0xfd5356bfu, 0x9b8ad070u, 0x39c24a21u, 0xd7f9c3d2u, 0x76313d83u,
    0x1468b734u, 0xb2a030e5u, 0x50d7aa96u, 0xef0f2447u, 0x8d469df8u, 0x2b7e17a9u, 0xc9b5915au, 0x67ed0b0bu,
    0x062484bcu, 0xa45bfe6du, 0x4293781eu, 0xe0caf1cfu, 0x7f026b80u, 0x1d39e531u, 0xbb715ee2u, 0x59a8d893u,
    0xf7e05244u, 0x9617cbf5u, 0x344f45a6u, 0xd286bf57u, 0x70be3908u, 0x0ef5b2b9u, 0xad2d2c6au, 0x4b64a61bu,
    0xe99c1fccu, 0x87d3997du, 0x260b132eu, 0xc4428cdfu, 0x627a0690u, 0x00b18041u, 0x9ee8f9f2u, 0x3d2073a3u,
    0xdb57ed54u, 0x798f6705u, 0x17c6e0b6u, 0xb5fe5a67u, 0x5435d418u, 0xf26d4dc9u, 0x90a4c77au, 0x2edc412bu,
    0xcd13badcu, 0x6b4b348du, 0x0982ae3eu, 0xa7ba27efu, 0x45f1a1a0u, 0xe4291b51u, 0x82609502u, 0x20980eb3u,
];

pub const BSHIM_256_TAB5: [u32; 96] = [
    0xebb0fac5u, 0x89e87476u, 0x281fee27u, 0xc65767d8u, 0x648ee189u, 0x02c65b3au, 0xa0fdd4ebu, 0x3f354e9cu,
    0xdd6cc84du, 0x7ba441feu, 0x19dbbbafu, 0xb8133560u, 0x564aaf11u, 0xf48228c2u, 0x92b9a273u, 0x30f11c24u,
    0xcf2895d5u, 0x6d600f86u, 0x0b978937u, 0xa9cf02e8u, 0x48067c99u, 0xe63df64au, 0x84756ffbu, 0x22ace9acu,
    0xc0e4635du, 0x5f1bdd0eu, 0xfd5356bfu, 0x9b8ad070u, 0x39c24a21u, 0xd7f9c3d2u, 0x76313d83u, 0x1468b734u,
    0xb2a030e5u, 0x50d7aa96u, 0xef0f2447u, 0x8d469df8u, 0x2b7e17a9u, 0xc9b5915au, 0x67ed0b0bu, 0x062484bcu,
    0xa45bfe6du, 0x4293781eu, 0xe0caf1cfu, 0x7f026b80u, 0x1d39e531u, 0xbb715ee2u, 0x59a8d893u, 0xf7e05244u,
    0x9617cbf5u, 0x344f45a6u, 0xd286bf57u, 0x70be3908u, 0x0ef5b2b9u, 0xad2d2c6au, 0x4b64a61bu, 0xe99c1fccu,
    0x87d3997du, 0x260b132eu, 0xc4428cdfu, 0x627a0690u, 0x00b18041u, 0x9ee8f9f2u, 0x3d2073a3u, 0xdb57ed54u,
    0x798f6705u, 0x17c6e0b6u, 0xb5fe5a67u, 0x5435d418u, 0xf26d4dc9u, 0x90a4c77au, 0x2edc412bu, 0xcd13badcu,
    0x6b4b348du, 0x0982ae3eu, 0xa7ba27efu, 0x45f1a1a0u, 0xe4291b51u, 0x82609502u, 0x20980eb3u, 0xbecf8864u,
    0x5d070215u, 0xfb3e7bc6u, 0x9975f577u, 0x37ad6f28u, 0xd5e4e8d9u, 0x741c628au, 0x1253dc3bu, 0xb08b55ecu,
    0x4ec2cf9du, 0xecfa494eu, 0x8b31c2ffu, 0x29693cb0u, 0xc7a0b661u, 0x65d83012u, 0x040fa9c3u, 0xa2472374u,
];

pub const BSHIM_256_TAB6: [u32; 96] = [
    0x6d600f86u, 0x0b978937u, 0xa9cf02e8u, 0x48067c99u, 0xe63df64au, 0x84756ffbu, 0x22ace9acu, 0xc0e4635du,
    0x5f1bdd0eu, 0xfd5356bfu, 0x9b8ad070u, 0x39c24a21u, 0xd7f9c3d2u, 0x76313d83u, 0x1468b734u, 0xb2a030e5u,
    0x50d7aa96u, 0xef0f2447u, 0x8d469df8u, 0x2b7e17a9u, 0xc9b5915au, 0x67ed0b0bu, 0x062484bcu, 0xa45bfe6du,
    0x4293781eu, 0xe0caf1cfu, 0x7f026b80u, 0x1d39e531u, 0xbb715ee2u, 0x59a8d893u, 0xf7e05244u, 0x9617cbf5u,
    0x344f45a6u, 0xd286bf57u, 0x70be3908u, 0x0ef5b2b9u, 0xad2d2c6au, 0x4b64a61bu, 0xe99c1fccu, 0x87d3997du,
    0x260b132eu, 0xc4428cdfu, 0x627a0690u, 0x00b18041u, 0x9ee8f9f2u, 0x3d2073a3u, 0xdb57ed54u, 0x798f6705u,
    0x17c6e0b6u, 0xb5fe5a67u, 0x5435d418u, 0xf26d4dc9u, 0x90a4c77au, 0x2edc412bu, 0xcd13badcu, 0x6b4b348du,
    0x0982ae3eu, 0xa7ba27efu, 0x45f1a1a0u, 0xe4291b51u, 0x82609502u, 0x20980eb3u, 0xbecf8864u, 0x5d070215u,
    0xfb3e7bc6u, 0x9975f577u, 0x37ad6f28u, 0xd5e4e8d9u, 0x741c628au, 0x1253dc3bu, 0xb08b55ecu, 0x4ec2cf9du,
    0xecfa494eu, 0x8b31c2ffu, 0x29693cb0u, 0xc7a0b661u, 0x65d83012u, 0x040fa9c3u, 0xa2472374u, 0x407e9d25u,
    0xdeb616d6u, 0x7ced9087u, 0x1b250a38u, 0xb95c83e9u, 0x5793fd9au, 0xf5cb774bu, 0x9402f0fcu, 0x323a6aadu,
    0xd071e45eu, 0x6ea95e0fu, 0x0ce0d7c0u, 0xab185171u, 0x494fcb22u, 0xe78744d3u, 0x85bebe84u, 0x23f63835u,
];

pub const BSHIM_256_TAB7: [u32; 96] = [
    0xef0f2447u, 0x8d469df8u, 0x2b7e17a9u, 0xc9b5915au, 0x67ed0b0bu, 0x062484bcu, 0xa45bfe6du, 0x4293781eu,
    0xe0caf1cfu, 0x7f026b80u, 0x1d39e531u, 0xbb715ee2u, 0x59a8d893u, 0xf7e05244u, 0x9617cbf5u, 0x344f45a6u,
    0xd286bf57u, 0x70be3908u, 0x0ef5b2b9u, 0xad2d2c6au, 0x4b64a61bu, 0xe99c1fccu, 0x87d3997du, 0x260b132eu,
    0xc4428cdfu, 0x627a0690u, 0x00b18041u, 0x9ee8f9f2u, 0x3d2073a3u, 0xdb57ed54u, 0x798f6705u, 0x17c6e0b6u,
    0xb5fe5a67u, 0x5435d418u, 0xf26d4dc9u, 0x90a4c77au, 0x2edc412bu, 0xcd13badcu, 0x6b4b348du, 0x0982ae3eu,
    0xa7ba27efu, 0x45f1a1a0u, 0xe4291b51u, 0x82609502u, 0x20980eb3u, 0xbecf8864u, 0x5d070215u, 0xfb3e7bc6u,
    0x9975f577u, 0x37ad6f28u, 0xd5e4e8d9u, 0x741c628au, 0x1253dc3bu, 0xb08b55ecu, 0x4ec2cf9du, 0xecfa494eu,
    0x8b31c2ffu, 0x29693cb0u, 0xc7a0b661u, 0x65d83012u, 0x040fa9c3u, 0xa2472374u, 0x407e9d25u, 0xdeb616d6u,
    0x7ced9087u, 0x1b250a38u, 0xb95c83e9u, 0x5793fd9au, 0xf5cb774bu, 0x9402f0fcu, 0x323a6aadu, 0xd071e45eu,
    0x6ea95e0fu, 0x0ce0d7c0u, 0xab185171u, 0x494fcb22u, 0xe78744d3u, 0x85bebe84u, 0x23f63835u, 0xc22db1e6u,
    0x60652b97u, 0xfe9ca548u, 0x9cd41ef9u, 0x3b0b98aau, 0xd943125bu, 0x777a8c0cu, 0x15b205bdu, 0xb3e97f6eu,
    0x5220f91fu, 0xf05872d0u, 0x8e8fec81u, 0x2cc76632u, 0xcafedfe3u, 0x69365994u, 0x076dd345u, 0xa5a54cf6u,
];

pub struct Shim256 {
    pub head: u32,
    pub tail: u32,
    pub flags: u32,
}

impl Shim256 {
    pub fn new() -> Self {
        Self { head: 0, tail: 0, flags: 0x001eef00u }
    }

    pub fn mix0(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xebca7700u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix1(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x71b64177u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix2(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xf7a20beeu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix3(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x7d8dd665u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix4(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x0379a0dcu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix5(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x89656b53u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix6(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x0f5135cau;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix7(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x953d0041u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix8(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x1b28cab8u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix9(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xa114952fu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix10(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x27005fa6u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix11(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xacec2a1du;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix12(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x32d7f494u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix13(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xb8c3bf0bu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix14(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x3eaf8982u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix15(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xc49b53f9u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix16(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x4a871e70u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix17(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xd072e8e7u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix18(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x565eb35eu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix19(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xdc4a7dd5u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix20(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x6236484cu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix21(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xe82212c3u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix22(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x6e0ddd3au;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix23(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xf3f9a7b1u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix24(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x79e57228u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix25(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xffd13c9fu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix26(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x85bd0716u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB2[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix27(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x0ba8d18du;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB3[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix28(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x91949c04u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB4[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix29(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x1780667bu;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB5[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix30(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x9d6c30f2u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB6[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix31(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x2357fb69u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB7[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix32(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0xa943c5e0u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB0[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

    pub fn mix33(&self, seed: u32, buf: &[u8]) -> u32 {
        let mut acc = seed ^ 0x2f2f9057u;
        for (i, byte) in buf.iter().enumerate() {
            acc = acc.rotate_left(5) ^ (*byte as u32);
            acc = acc.wrapping_add(BSHIM_256_TAB1[((i as u32).wrapping_add(acc) & 95) as usize]);
        }
        acc
    }

}

