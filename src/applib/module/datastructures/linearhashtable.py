"""A Set implementation that uses hashing with linaer probing"""

from typing import Any, Iterable

from .utils import new_array
from .base import BaseSet

w = 32


class LinearHashTable(BaseSet):

    def __init__(self, iterable: Iterable = []):
        self._initialize()
        self.initialize()
        self.add_all(iterable)

    def __iter__(self):
        for x in self.t:
            if x is not None and x != self.dl:
                yield x

    def _initialize(self):
        self.dl = object()

    def _hash(self, x):
        h = self.hash_code(x)
        return (
            self.tab[0][h & 0xFF]
            ^ self.tab[1][(h >> 8) & 0xFF]
            ^ self.tab[2][(h >> 16) & 0xFF]
            ^ self.tab[3][(h >> 24) & 0xFF]
        ) >> (w - self.d)

    def _resize(self):
        self.d = 1
        while (1 << self.d) < 3 * self.n:
            self.d += 1
        told = self.t
        self.t = new_array((1 << self.d))
        self.q = self.n
        for x in told:
            if x is not None and x != self.dl:
                i = self._hash(x)
                while self.t[i] is not None:
                    i = (i + 1) % len(self.t)
                self.t[i] = x

    def initialize(self):
        self.d = 1
        self.t = new_array((1 << self.d))
        self.q = 0
        self.n = 0

    def hash_code(self, x):
        return hash(x)

    def add(self, x) -> bool:
        if self.find(x) is not None:
            return False
        if 2 * (self.q + 1) > len(self.t):
            self._resize()
        i = self._hash(x)
        while self.t[i] is not None and self.t[i] != self.dl:
            i = (i + 1) % len(self.t)
        if self.t[i] is None:
            self.q += 1
        self.n += 1
        self.t[i] = x
        return True

    def find(self, x) -> Any | None:
        i = self._hash(x)
        while self.t[i] is not None:
            if self.t[i] != self.dl and x == self.t[i]:
                return self.t[i]
            i = (i + 1) % len(self.t)

    def remove(self, x):
        i = self._hash(x)
        while self.t[i] is not None:
            y = self.t[i]
            if y != self.dl and x == y:
                self.t[i] = self.dl
                self.n -= 1
                if 8 * self.n < len(self.t):
                    self._resize()
                return y
            i = (i + 1) % len(self.t)
        return None

    def clear(self):
        self.initialize()

    """Fake sample code:

    def add_slow(self, x):
        if 2*(self.q+1) > len(self.t): resize()
        i = self._hash(x)
        while self.t[i] is not None:
            if self.t[1] != self.dl and x == self.t[i]: return False
            i = (i + 1) % len(self.t[i])
        t[i] = x
        self.n += 1
        self.q += 1
        return True

    def ideal_hash(self, x):
        return tab[x.hashCode() >> w-d]
    """

    """A bunch of random values for use in tabulation hashing"""
    tab = [
        [
            0x0069AEFF,
            0x6AC0719E,
            0x384CD7EE,
            0xCBA78313,
            0x133EF89A,
            0xB37979E6,
            0xA4C4E09C,
            0x911C738B,
            0xC7FE9194,
            0xBA8E5DC7,
            0xE610718C,
            0x48460AC5,
            0x6B4D9D43,
            0x73AFEEAB,
            0x051264CB,
            0x4B3DBA93,
            0x28837665,
            0xFB80A52B,
            0xAD1C14AF,
            0xB2BAF17F,
            0x35E311A5,
            0xF7FA2905,
            0xA973C315,
            0x00885F47,
            0x8842622B,
            0x0445A92C,
            0x701BA3A0,
            0xEF608902,
            0x176099AD,
            0xD240F938,
            0xB32D83C6,
            0xB341AFB8,
            0xC3A978FB,
            0x55ED1F0C,
            0xB581286E,
            0x8FF6938E,
            0x9F11C1C5,
            0x4D083BD6,
            0x1AACC2A4,
            0xDF13F00A,
            0x1E282712,
            0x772D354B,
            0x21E3A7FD,
            0x4BC932DC,
            0xE1DEB7BA,
            0x5E868B8A,
            0xC9331CC6,
            0xAA931BBF,
            0xFF92ABA6,
            0xE3EFC69F,
            0xDA3B8E2A,
            0xF9B21EC1,
            0x2FB89674,
            0x61C87462,
            0xA553C2F9,
            0xCA01E279,
            0x35999337,
            0xF44C4FD3,
            0x136A2773,
            0x812607A8,
            0xBFCD9BBF,
            0x0B1D15CD,
            0xC2A0038B,
            0x029AB4F7,
            0xCD7C58F9,
            0xED3821C4,
            0x325457C6,
            0x1DC6B295,
            0x876DCB83,
            0x52DF45FC,
            0xA01C9FBA,
            0xC938FF66,
            0x19E52C87,
            0x03AE67F9,
            0x7DB39E51,
            0x74F31686,
            0x5F10E5A3,
            0x74108D8A,
            0x64E63104,
            0xD86A38D6,
            0x65BE2FBB,
            0xEF06049E,
            0x9BCA1DBD,
            0x06C63E73,
            0xE97BD103,
            0xFED3C22C,
            0x09D10FC6,
            0xB92633A3,
            0x21378EBF,
            0xE37FA54E,
            0x893C7910,
            0xC1C74A5A,
            0x6C23C029,
            0x4D4B6187,
            0xD72BB8FB,
            0x0DBE1118,
            0x5E0F4188,
            0xCE0D2DC8,
            0x8DD83231,
            0x0466AB90,
            0x814BC11A,
            0xEF688B9B,
            0x0A03C851,
            0xCA3C984F,
            0x6DF87CA4,
            0x6B34D1B2,
            0x2BAD5C75,
            0xAED1B6D8,
            0x8C73F8B4,
            0x4577D798,
            0x5C953767,
            0xE7DA2D51,
            0x2B9279A0,
            0x418D9B51,
            0x8C47EC3D,
            0x894E6119,
            0xA0CA769D,
            0x1C3B16A4,
            0xA1621B5B,
            0xA695DA53,
            0x22462819,
            0xF4B878CF,
            0x72B4D648,
            0x1FAF4267,
            0x4BA16750,
            0x08A9D645,
            0x6BFB829C,
            0xE051295F,
            0x6DD5CD97,
            0x2E9D1BAF,
            0x6ED6231D,
            0x6F84CB25,
            0x9AE60C95,
            0xBCEE55CA,
            0x6831CD97,
            0x2CCDBC99,
            0x9F8A0A81,
            0xA0B2C08F,
            0xE957C36B,
            0x9CB797B5,
            0x107C6362,
            0x48DACF5D,
            0x6E16F569,
            0x39BE78C3,
            0x6445637F,
            0xED445EE5,
            0x8EC45004,
            0x9EF8A405,
            0xB5796A45,
            0x049D5143,
            0xB3C1D852,
            0xC36D9B44,
            0xAB0DA981,
            0xFF5226B3,
            0x19169B4C,
            0x9A49194D,
            0xBA218B42,
            0xAB98C8EE,
            0x4DB02645,
            0x6FACA3C8,
            0x12C60D2D,
            0xAF67B750,
            0xF0F6A855,
            0xEAD566D9,
            0x42D0CCCD,
            0x76A532BB,
            0x82A6DC35,
            0xC1C23D0E,
            0x83D45BD2,
            0xD7024912,
            0x97888901,
            0x2B7CDD2C,
            0x523742A5,
            0xECB96B3B,
            0xD800D833,
            0x7B4D0C91,
            0x95C7DD86,
            0x88880AAD,
            0xF0CE0990,
            0x7E292A90,
            0x79AC4437,
            0x8A9F59CC,
            0x818444D1,
            0xAE4E735D,
            0xA529DB95,
            0x58B35661,
            0xA909A7DE,
            0x9273BEAA,
            0xFE94332C,
            0x259B88E4,
            0xC88F4F6A,
            0x2A9D33EF,
            0x4B5D106D,
            0xDC3A9FCA,
            0xA8061CAD,
            0x7679422C,
            0xAF72AD02,
            0xC5799EA5,
            0x306D694D,
            0x620AAD10,
            0xD188B9DD,
            0xEFF6AD87,
            0x6B890354,
            0xB5907CD3,
            0x733290FC,
            0x4B6C0733,
            0x0BAD0EBD,
            0xA049D3AD,
            0xC9D0CDAE,
            0x9C144D6F,
            0x5990B63B,
            0xFA33D8E2,
            0x9EBEB5A0,
            0xBC7C5C92,
            0xD3EDD2E6,
            0x54AE1AF6,
            0xD6ADA4BD,
            0x14094C5A,
            0x0E3C5ADF,
            0xF1AB60F1,
            0x74456A66,
            0x0F3A675A,
            0x87445D0D,
            0xA81ADC2E,
            0x0F47A1A5,
            0x4EEDB844,
            0x9C9CB0CE,
            0x8BB3D330,
            0x02DF93E6,
            0x86E3AD51,
            0x1C1072B9,
            0xACF3001B,
            0xBD08C487,
            0xC2667A11,
            0xDD5EF664,
            0xD47B67FB,
            0x959CCA45,
            0xA7DA8E68,
            0xB75B1E18,
            0x75201924,
            0xE689AB8B,
            0x0F5E6B0A,
            0x75205923,
            0xBBA35593,
            0xD24DAB24,
            0x0288CAEB,
            0xCBF022A9,
            0x392D7EE5,
            0x16FE493A,
            0xB6BCADFD,
            0x9813EC72,
            0x9AA3D37C,
            0xEE88A59E,
            0x6CDBAD4E,
            0x6B96AABF,
            0xCB54D5E5,
        ],
        [
            0x116FC403,
            0x260D7E7B,
            0xDEF689E7,
            0xA5B3D49A,
            0x921F3594,
            0xB24C8CBA,
            0x1BDEFB3F,
            0x6519E846,
            0x24B37253,
            0x1CC6B12B,
            0x6F48F06E,
            0xCA90B0DB,
            0x8E20570B,
            0xDA75ED0F,
            0x1B515143,
            0x0990A659,
            0xDCEDB6B3,
            0xEC22DE79,
            0xDD56F7A9,
            0x901194A6,
            0x4BF3DB02,
            0x5D31787D,
            0xD24DA2CA,
            0x9FC9BC14,
            0x9AA38AC9,
            0xE95972BA,
            0x8233A732,
            0xB9D4317E,
            0x51F9B329,
            0x94F12C56,
            0x1ACE26E4,
            0xECDA5183,
            0x1353E547,
            0x39B99AB3,
            0x6413AC97,
            0xEB6B5334,
            0xDD94ED2B,
            0x298E9D2C,
            0xD38ABC91,
            0x3F17EE4E,
            0x99F8931D,
            0x88BAE7DA,
            0xB5506A36,
            0x2D7BAF6D,
            0x42A98D2B,
            0xBB9B94B9,
            0x58820083,
            0x521BBA4C,
            0x76699597,
            0x137B86BE,
            0x8533888E,
            0xB37316DD,
            0x284C3DE4,
            0xFE60E3E6,
            0x94EDAA40,
            0x919C85CD,
            0x24CB6F23,
            0x6B446FBD,
            0xBE933C15,
            0x2A43951A,
            0x791A9F90,
            0x47977C04,
            0xA6350EEC,
            0x95E817A5,
            0xFFC82E8C,
            0xAD379229,
            0x6EC9531A,
            0x8CAB29F9,
            0xB2F18402,
            0xD0EBDAC1,
            0xD7B559B4,
            0x7AD30E7C,
            0xE1D1ADB7,
            0x58A66F9C,
            0x7A26636A,
            0x8C865F92,
            0x65363517,
            0x732B87DB,
            0x64A1AD52,
            0x72E87C39,
            0x0B943E4D,
            0x532D3593,
            0xEDCF9975,
            0x44B5BEC1,
            0x13AC91F8,
            0x6E6F3A76,
            0x36AC3C6D,
            0x528A3ECF,
            0xF3D8CD75,
            0x8FACD64C,
            0xDB4D13D5,
            0x80D49A67,
            0xAA7061D3,
            0x9486BA8D,
            0x7454A65B,
            0x18E7B707,
            0xD9CC05B9,
            0x44EB014D,
            0x28BA26D8,
            0xA8852791,
            0xF8DC3053,
            0xABE46B52,
            0x9E261D1F,
            0x768F83DD,
            0x1C888838,
            0x6D9B9CE6,
            0x69E82575,
            0x2959538F,
            0xD0FF9685,
            0x92B4540C,
            0x7C93035B,
            0x7CAD90AD,
            0x49AAA908,
            0x3981F4B8,
            0x191F4339,
            0xD0971BFC,
            0xA7209692,
            0x0E253CAD,
            0x40E2EE61,
            0xC5C63486,
            0xDF4F238B,
            0x2D3CB89A,
            0x3B5704B2,
            0xCC14C2CB,
            0xB1698D38,
            0x079C3B9B,
            0xBB3867E4,
            0x9F01E223,
            0x35E69012,
            0x5C87D888,
            0x2CEA4193,
            0xEE088DA5,
            0x0EA4D5AB,
            0x8A4906E8,
            0xF6E5E283,
            0xEE87FA18,
            0x9F96C751,
            0x947252C0,
            0x9B50B97E,
            0x05952521,
            0x9440F5AE,
            0xA0642786,
            0xEBCC62BE,
            0xADCCF011,
            0x00B863E6,
            0x1C3AB5B3,
            0x7C701E4B,
            0xA9565792,
            0xB1AD459C,
            0x833BA164,
            0x89544AE3,
            0x35540C75,
            0x198D0FEC,
            0xBE93BF33,
            0xC28444B3,
            0xBC3ADD48,
            0xB4300C14,
            0xEE0ED408,
            0xCA08ADA3,
            0x0BE06480,
            0xC4DD8CE2,
            0x61195564,
            0x5B10A111,
            0x65CD2B3B,
            0xCBEB06AE,
            0xFCE70080,
            0xEF40B102,
            0xFC0BFE6F,
            0x8111BF20,
            0xFB166DB1,
            0x3598B2EF,
            0x1E0E04DE,
            0x1BF7CF2D,
            0x0DE7EAF1,
            0x829457E0,
            0xE8865341,
            0x826272AD,
            0xB57DB2A4,
            0x7413E6E7,
            0x416323FF,
            0x8E08D503,
            0x1DA4DFAC,
            0x983B9A78,
            0x0FAB5FE0,
            0x585E7A90,
            0x038CF73C,
            0xECF90D31,
            0x046055C8,
            0x59926D71,
            0x06959F1F,
            0x3B8290B7,
            0x0BB834D9,
            0xA0DC5BEC,
            0xEC9AE604,
            0x6EBFD59D,
            0xFECCBAB5,
            0x240BD4BA,
            0x2DF2B232,
            0xE14E0383,
            0xD86526EC,
            0xE3D974FC,
            0x940662B5,
            0x81ABF5D4,
            0x8010E6EB,
            0x700D9849,
            0x040D0C42,
            0xC980417B,
            0x95FA374A,
            0x724B1448,
            0x217205EC,
            0x0153B4BB,
            0xEA55EA92,
            0x2049D5A1,
            0x82576F06,
            0x586FCFEB,
            0xA975E489,
            0x14C862E9,
            0xACB8B52C,
            0x2F3FB91E,
            0xCE273650,
            0x66608F4A,
            0x24F81BB7,
            0x0382DC34,
            0x07BDC163,
            0xC42AD034,
            0xE63CF998,
            0x1A61F233,
            0xD5754EBE,
            0x37275214,
            0x2322DE2A,
            0x3A53B9B4,
            0xAB9C6963,
            0x2F3A51BE,
            0x5066E7C7,
            0x941BDA97,
            0x75FADCEB,
            0xD05AD081,
            0xF77D5DAF,
            0xD9879250,
            0xEBF8BF97,
            0x65BE4A70,
            0x388EDA48,
            0x728173FB,
            0x05975BFA,
            0x314DAD8A,
            0x2CB4909F,
            0xC736B716,
            0x9007296D,
            0x4FD61551,
            0xD4378CCF,
            0x649AAC3E,
            0xD9CA1A9D,
            0x16FF16AE,
            0x8090F1C5,
            0xFE0C4703,
            0xC4152307,
        ],
        [
            0xF07E5E34,
            0x62114BA6,
            0xF45FFE22,
            0xBAA48702,
            0xE27E48A4,
            0xC43B4779,
            0x549A4566,
            0x93BC4836,
            0x3B2E8D46,
            0x3F8A77AE,
            0x71E2D944,
            0xC09C5DCE,
            0xEBFBFD4F,
            0x7F8E1C40,
            0x3C310A69,
            0x52F62F09,
            0xB7FD11BB,
            0xA9D055A7,
            0xE3BD4654,
            0x9696AE10,
            0xDF953225,
            0x42FD2380,
            0x69756E5C,
            0x9D950BC4,
            0xE2BEEA59,
            0xD33DAA07,
            0xE97D31CE,
            0xD9FB0A49,
            0x553A27F2,
            0x7166586F,
            0xEB04D48C,
            0x72ADB63A,
            0x340AB99E,
            0x459B4609,
            0x481421B7,
            0x7DB83C71,
            0x192F6C22,
            0x711852A8,
            0xC6BD6562,
            0xB91BE2C8,
            0xEFE89DBF,
            0xC404EB9B,
            0x9EBC1BC7,
            0x8DC7EED2,
            0x4D84EFD7,
            0x0783D7E5,
            0x3B5CA2F2,
            0x9997E51C,
            0x89B432C9,
            0x72AE9672,
            0x61D522D9,
            0xA639FD45,
            0xA7DA3B46,
            0x696E73EC,
            0x89581A95,
            0x4AA25F94,
            0xD0EB2A48,
            0x04865F68,
            0x1CBD651A,
            0xD6B2AFD9,
            0xD401B965,
            0xD20AA5A7,
            0xC0AA1B15,
            0xFB4CE7AF,
            0x159974C5,
            0x15D0841D,
            0x6B2836B4,
            0xEF3B3EDF,
            0xAF2DB0B3,
            0x13106FB6,
            0xFF41D7F9,
            0xAB2A698D,
            0x68E04DC9,
            0xE5EE0099,
            0xE50D4017,
            0x5EA78D6D,
            0x2E18FB07,
            0xFE22B9FF,
            0x544C05F1,
            0xC2E10853,
            0x8D151BD6,
            0x17EE763A,
            0xA663CE31,
            0x4A4B5E33,
            0x298B13C1,
            0xD3B40C89,
            0x121B6B4E,
            0x59CF0429,
            0x3D0BAB9D,
            0xD24C5DFE,
            0x5BB7349F,
            0xAC5DBFE9,
            0x7ECA5EBB,
            0xADB8B3E3,
            0x71AB540B,
            0xC8E3DC0D,
            0x12E6CD3F,
            0x8197F22C,
            0x5FF77265,
            0xE5641DBC,
            0x818AB24C,
            0x627B98F7,
            0xDD84E1D6,
            0x531C2346,
            0xEC2F4E3C,
            0x4A3CB318,
            0x70CB24FE,
            0x35C17BFE,
            0xEC91FD18,
            0x6EFB3C18,
            0x16908369,
            0x41732188,
            0x449E658B,
            0x2E9931CB,
            0x67CD066E,
            0x883CA306,
            0xF66AECAC,
            0x979BF015,
            0x8E85E27D,
            0x0560372B,
            0x987995D6,
            0xAFF98ED7,
            0x552EE87B,
            0x21A53787,
            0x3D3CFD45,
            0xA084DAE0,
            0x8C91BE2F,
            0xAC4C3550,
            0xA7DB63FF,
            0x124B2F23,
            0x95D05D4E,
            0xB983DB13,
            0xA929A3C1,
            0x111CD0A0,
            0xF59DED9A,
            0xCE677AE3,
            0xFA949E59,
            0xD673E658,
            0xF8C8E27B,
            0x3C60FC3D,
            0x59A4F230,
            0xF54A5E87,
            0x08CFF440,
            0xD4BBB1EE,
            0x6A0C7DB0,
            0xECBAA99D,
            0xEC61DCAF,
            0xF1056E2B,
            0x54236899,
            0xADAD347C,
            0xC9885BC9,
            0x2FE2A4EC,
            0x01BA2B86,
            0x6B23F604,
            0xB354EF08,
            0x6A3DC5E2,
            0xAB61DA36,
            0x7543925A,
            0x0A558940,
            0x48D4D8F3,
            0xD84F2F6F,
            0x6AC5311C,
            0xCD1B660E,
            0x51293D3D,
            0xA0F15790,
            0xD629CD78,
            0x89201FA5,
            0x46005119,
            0x9617FA14,
            0xC375A68B,
            0x7CCB519B,
            0x6420A714,
            0xB736D2CE,
            0x154FCF4A,
            0x71CAD2F5,
            0xACB150D7,
            0x97BC8E36,
            0xC5506D0A,
            0xA9FACC35,
            0x1A9630DB,
            0xBD3D72EE,
            0x58CDF27C,
            0x17F3E1F9,
            0x41598836,
            0xD6ADAC30,
            0x309A5B3F,
            0x3BD3AA32,
            0x40F08F50,
            0xF37CBD6C,
            0xCBDB8AEF,
            0xE0819189,
            0x5A9B663B,
            0x6932A448,
            0xB1B3E866,
            0xC50EE24D,
            0xAD999126,
            0xAFB04056,
            0xC95974E5,
            0x636A64FA,
            0x0BB12DD9,
            0x78CAA164,
            0xD26A7EC8,
            0x451A0B53,
            0x6D00AAC6,
            0x484D1D9D,
            0x39728DD4,
            0xFBFEC2EA,
            0xA6D5AAF9,
            0x91C4F6EA,
            0x31CAB009,
            0x9B6BA4E8,
            0xE271ED67,
            0x4C87A84D,
            0x8A1A4567,
            0x93749497,
            0xC566EDCC,
            0xC8229554,
            0x927925FD,
            0xAD1CACED,
            0xDC24F7ED,
            0xC92B9220,
            0x936CD037,
            0xBD2D0256,
            0x5C92409B,
            0xA3AA2682,
            0x4DA97646,
            0xBCFDEC81,
            0x25D5B61D,
            0x20E1660D,
            0x4B5214ED,
            0x91AA596A,
            0xB241415C,
            0x88EC91A1,
            0x2375E939,
            0x981AD627,
            0x4A54EE18,
            0x13D98660,
            0x9375C64D,
            0x538D3B28,
            0x4BF37CA7,
            0x192B351E,
            0x3CACF215,
            0x3ECF3565,
            0x50F5C0FC,
            0xAAFE3D4E,
            0x6351B4F5,
            0x1B800D4F,
            0xFAD73CDF,
            0xE300E1D8,
            0xB2CB5B04,
            0xFB019702,
            0xFB647F85,
            0x375A7B74,
            0xED6A6760,
            0x45C54E76,
            0x06524D79,
        ],
        [
            0x48722EC4,
            0x8A2694DB,
            0x3CF80478,
            0xF9BC47BA,
            0x76B258FB,
            0xF71A1EC6,
            0x841189DF,
            0x1A866461,
            0x72B5488C,
            0x71663983,
            0xBDA59407,
            0xA2B68F85,
            0x62DBD0AA,
            0xE4966AA3,
            0x32E0EFAA,
            0x71BB3699,
            0x2EDA14A6,
            0x53F8917C,
            0x874974CE,
            0xE680BCCA,
            0x96A9C462,
            0x399CA451,
            0xC46616F5,
            0xEEE71114,
            0x5878E472,
            0x3A83C559,
            0x54862A18,
            0x82AEA480,
            0x492D0019,
            0xD62A7027,
            0x36655F50,
            0xCE412FDF,
            0xC8136871,
            0xD6CFE1D8,
            0x121C9C91,
            0x13ABBF51,
            0x3AAA7037,
            0x9F6E7CB6,
            0xAE82C4C4,
            0x55FDCE32,
            0xD8DD6BDA,
            0xD6EC4938,
            0x6A5AEE52,
            0x52C8A764,
            0xA6A85297,
            0x5131DE9E,
            0x396A6599,
            0xE27B1100,
            0xE68588D3,
            0x7B89A612,
            0xAD48A7A4,
            0xFD205673,
            0x81807089,
            0x239D2D38,
            0x39518DF3,
            0x256F3F14,
            0x5C65E7B8,
            0x64CAEBDC,
            0xD8D694B6,
            0xB4A87DA3,
            0xA651881E,
            0xCA1D252D,
            0x993A3DDC,
            0x14F9A54D,
            0x6B14D2FF,
            0xBBED03BB,
            0x8D12BC03,
            0x6CCE455D,
            0x613D6487,
            0x6D04CE6A,
            0xC2F4C84C,
            0x306D8FF2,
            0x584A9847,
            0x68902FC5,
            0x70AF1A4F,
            0x3AB4CB98,
            0xE8BE4453,
            0x7E95D355,
            0x84B0F371,
            0x4C5CCB52,
            0xDD6D029C,
            0xAFA47124,
            0x71AABF91,
            0xD3407F95,
            0xE7FA3A9C,
            0x4F634405,
            0x0CBF2CB7,
            0x0192FF17,
            0x296959DD,
            0x9E4D34D5,
            0xFD9A4286,
            0xAC7B6933,
            0x4650F585,
            0x168AF40D,
            0x73816119,
            0x5542D96D,
            0x99047276,
            0x1B5BBE67,
            0x01A8209E,
            0x6F9DB32E,
            0xD762BBD1,
            0x299A3804,
            0x87ABE66D,
            0xD479EEAA,
            0x79928F4E,
            0x3937FFBC,
            0x3C8E83CA,
            0x2A8F9347,
            0x4D2324D3,
            0xF0183DDA,
            0x9FBEDB15,
            0xAC365889,
            0xF1BE552C,
            0xA4B32D5A,
            0xDC77FFF3,
            0x9D516DA8,
            0x7F3C347C,
            0x39E8479F,
            0x9E869687,
            0x6A160347,
            0x49AB7403,
            0x830D31C7,
            0x11311354,
            0x79E6CC69,
            0x35B25CAA,
            0x398AF9AA,
            0x02EF4356,
            0xB5ECBA53,
            0x666D6C8B,
            0x8836B3AE,
            0x23B9FC98,
            0x0CC8E3D0,
            0x3AD594E1,
            0xB124529D,
            0xE059C1DE,
            0xFA88E0D9,
            0xBA117846,
            0x1782A65A,
            0xEE9F80F9,
            0xBC9AEC55,
            0x88AEC1D4,
            0x9C3907FA,
            0x92B7B5BF,
            0x464ACBF4,
            0xBBBD04A8,
            0xF0E966BF,
            0x14C5F971,
            0x83018D49,
            0xFAF4FC0A,
            0x3B4639B2,
            0x6B7E297D,
            0xC0E9A807,
            0x418713D3,
            0x1A2B2361,
            0x80850D90,
            0xD515816E,
            0x3DEB48EA,
            0x6BFE6AA1,
            0x3680036C,
            0x228E76AE,
            0x78F16C87,
            0xFF4D85EA,
            0x7D831974,
            0xBA962D6B,
            0x4BAE0B1D,
            0xC0DB431A,
            0x04B46400,
            0xCF427175,
            0x244E321D,
            0x1C8B1FC9,
            0x63A2B794,
            0x1939D9C6,
            0xC92A530E,
            0x21A8E5AD,
            0x28050194,
            0x3B106223,
            0xB21E2CE1,
            0x7AE71FE4,
            0x7F7759F0,
            0x0329C8F4,
            0xD09F6B37,
            0x897E12A5,
            0x4103C4B1,
            0x56520DAE,
            0x5D7391AA,
            0x7AC9F12D,
            0xEAC6B834,
            0x99F8F6A8,
            0x2867867A,
            0xFF6F3343,
            0x3167097A,
            0x38432D1D,
            0x108377F8,
            0xFD8E0D5F,
            0x25E15692,
            0xF00D40F9,
            0x1F1276F3,
            0xB748C8CD,
            0x6DBB9D9C,
            0x99AB7CEB,
            0xA4A9784F,
            0xCB4B2535,
            0xB3EB5CA7,
            0xD3A09E75,
            0x90F3EE7E,
            0x28EF2A57,
            0xBDB643A2,
            0x1112AB10,
            0x546B1AF2,
            0x8C41E90D,
            0x0F5FCD88,
            0x6F259F40,
            0x34B33966,
            0x5F3558D7,
            0xFFF36F0B,
            0xA3459449,
            0xDCECBCE1,
            0x69FF2BF7,
            0x7525E1DA,
            0x24C9DE72,
            0xEA9626B1,
            0x87C7385D,
            0x15E4211E,
            0x9F7EF269,
            0xFED018D1,
            0x7632076C,
            0x8D4F0157,
            0x10C1205A,
            0x65DB0E00,
            0x813F0E8B,
            0xBAFEA255,
            0xB47E6663,
            0x2A0EBA78,
            0xF66B3783,
            0xFFF1DB48,
            0x47997F03,
            0x3A49E877,
            0x4536A0B5,
            0x89B0738F,
            0xF5758B5E,
            0x1D277388,
            0xF5DB28E8,
            0xB4EF0ADD,
            0x776FED12,
            0x045B614A,
            0xC95F47AE,
            0x13A1D602,
            0x217D6338,
            0xC509D080,
            0x006789DE,
            0xD891CCCC,
            0xB02F9980,
            0x67F00301,
            0xAFC87999,
            0x043D8FBD,
            0xB32D6061,
        ],
    ]
