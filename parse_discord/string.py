"""String operations which emulate internal Discord operations. Not exported."""

from __future__ import annotations

import codecs
from typing import Iterator, TYPE_CHECKING

import regex
from urllib import parse

from ada_url import URL

from .ast import *

if TYPE_CHECKING:
    from .parse import Context


def text_to_url(s: str, /) -> URL | None:
    """Parse a string as a WHATWG URL, returning None if the URL is invalid or the scheme is not allowed by Discord."""
    if not URL.can_parse(s):
        return None
    u = URL(s)
    if u.protocol not in ("http:", "https:", "discord:"):
        return None
    return u

IncrementalDecoder = codecs.getincrementaldecoder("utf-8")
SAFE = frozenset('"-0123456789<>ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz~‎‏‪‫‬‭‮؜⁦⁧⁨⁩🔏🔐🔒🔓                 　⠀­͏؀؁؂؃؄؅۝܏࣢ᅟᅠ឴឵᠋᠌᠍᠎​‌‍⁠⁡⁢⁣⁤⁥⁪⁫⁬⁭⁮⁯ㅤ￰￱￲￳￴￵￶￷￸︀︁︂︃︄︅︆︇︈︉︊︋︌︍︎️﻿ﾠ￹￺￻𑂽𑃍𓐰𓐱𓐲𓐳𓐴𓐵𓐶𓐷𓐸𛲠𛲡𛲢𛲣𝅳𝅴𝅵𝅶𝅷𝅸𝅹𝅺󠀀󠀁󠀂󠀃󠀄󠀅󠀆󠀇󠀈󠀉󠀊󠀋󠀌󠀍󠀎󠀏󠀐󠀑󠀒󠀓󠀔󠀕󠀖󠀗󠀘󠀙󠀚󠀛󠀜󠀝󠀞󠀟󠀠󠀡󠀢󠀣󠀤󠀥󠀦󠀧󠀨󠀩󠀪󠀫󠀬󠀭󠀮󠀯󠀰󠀱󠀲󠀳󠀴󠀵󠀶󠀷󠀸󠀹󠀺󠀻󠀼󠀽󠀾󠀿󠁀󠁁󠁂󠁃󠁄󠁅󠁆󠁇󠁈󠁉󠁊󠁋󠁌󠁍󠁎󠁏󠁐󠁑󠁒󠁓󠁔󠁕󠁖󠁗󠁘󠁙󠁚󠁛󠁜󠁝󠁞󠁟󠁠󠁡󠁢󠁣󠁤󠁥󠁦󠁧󠁨󠁩󠁪󠁫󠁬󠁭󠁮󠁯󠁰󠁱󠁲󠁳󠁴󠁵󠁶󠁷󠁸󠁹󠁺󠁻󠁼󠁽󠁾󠁿󠂀󠂁󠂂󠂃󠂄󠂅󠂆󠂇󠂈󠂉󠂊󠂋󠂌󠂍󠂎󠂏󠂐󠂑󠂒󠂓󠂔󠂕󠂖󠂗󠂘󠂙󠂚󠂛󠂜󠂝󠂞󠂟󠂠󠂡󠂢󠂣󠂤󠂥󠂦󠂧󠂨󠂩󠂪󠂫󠂬󠂭󠂮󠂯󠂰󠂱󠂲󠂳󠂴󠂵󠂶󠂷󠂸󠂹󠂺󠂻󠂼󠂽󠂾󠂿󠃀󠃁󠃂󠃃󠃄󠃅󠃆󠃇󠃈󠃉󠃊󠃋󠃌󠃍󠃎󠃏󠃐󠃑󠃒󠃓󠃔󠃕󠃖󠃗󠃘󠃙󠃚󠃛󠃜󠃝󠃞󠃟󠃠󠃡󠃢󠃣󠃤󠃥󠃦󠃧󠃨󠃩󠃪󠃫󠃬󠃭󠃮󠃯󠃰󠃱󠃲󠃳󠃴󠃵󠃶󠃷󠃸󠃹󠃺󠃻󠃼󠃽󠃾󠃿󠄀󠄁󠄂󠄃󠄄󠄅󠄆󠄇󠄈󠄉󠄊󠄋󠄌󠄍󠄎󠄏󠄐󠄑󠄒󠄓󠄔󠄕󠄖󠄗󠄘󠄙󠄚󠄛󠄜󠄝󠄞󠄟󠄠󠄡󠄢󠄣󠄤󠄥󠄦󠄧󠄨󠄩󠄪󠄫󠄬󠄭󠄮󠄯󠄰󠄱󠄲󠄳󠄴󠄵󠄶󠄷󠄸󠄹󠄺󠄻󠄼󠄽󠄾󠄿󠅀󠅁󠅂󠅃󠅄󠅅󠅆󠅇󠅈󠅉󠅊󠅋󠅌󠅍󠅎󠅏󠅐󠅑󠅒󠅓󠅔󠅕󠅖󠅗󠅘󠅙󠅚󠅛󠅜󠅝󠅞󠅟󠅠󠅡󠅢󠅣󠅤󠅥󠅦󠅧󠅨󠅩󠅪󠅫󠅬󠅭󠅮󠅯󠅰󠅱󠅲󠅳󠅴󠅵󠅶󠅷󠅸󠅹󠅺󠅻󠅼󠅽󠅾󠅿󠆀󠆁󠆂󠆃󠆄󠆅󠆆󠆇󠆈󠆉󠆊󠆋󠆌󠆍󠆎󠆏󠆐󠆑󠆒󠆓󠆔󠆕󠆖󠆗󠆘󠆙󠆚󠆛󠆜󠆝󠆞󠆟󠆠󠆡󠆢󠆣󠆤󠆥󠆦󠆧󠆨󠆩󠆪󠆫󠆬󠆭󠆮󠆯󠆰󠆱󠆲󠆳󠆴󠆵󠆶󠆷󠆸󠆹󠆺󠆻󠆼󠆽󠆾󠆿󠇀󠇁󠇂󠇃󠇄󠇅󠇆󠇇󠇈󠇉󠇊󠇋󠇌󠇍󠇎󠇏󠇐󠇑󠇒󠇓󠇔󠇕󠇖󠇗󠇘󠇙󠇚󠇛󠇜󠇝󠇞󠇟󠇠󠇡󠇢󠇣󠇤󠇥󠇦󠇧󠇨󠇩󠇪󠇫󠇬󠇭󠇮󠇯󠇰󠇱󠇲󠇳󠇴󠇵󠇶󠇷󠇸󠇹󠇺󠇻󠇼󠇽󠇾󠇿󠈀󠈁󠈂󠈃󠈄󠈅󠈆󠈇󠈈󠈉󠈊󠈋󠈌󠈍󠈎󠈏󠈐󠈑󠈒󠈓󠈔󠈕󠈖󠈗󠈘󠈙󠈚󠈛󠈜󠈝󠈞󠈟󠈠󠈡󠈢󠈣󠈤󠈥󠈦󠈧󠈨󠈩󠈪󠈫󠈬󠈭󠈮󠈯󠈰󠈱󠈲󠈳󠈴󠈵󠈶󠈷󠈸󠈹󠈺󠈻󠈼󠈽󠈾󠈿󠉀󠉁󠉂󠉃󠉄󠉅󠉆󠉇󠉈󠉉󠉊󠉋󠉌󠉍󠉎󠉏󠉐󠉑󠉒󠉓󠉔󠉕󠉖󠉗󠉘󠉙󠉚󠉛󠉜󠉝󠉞󠉟󠉠󠉡󠉢󠉣󠉤󠉥󠉦󠉧󠉨󠉩󠉪󠉫󠉬󠉭󠉮󠉯󠉰󠉱󠉲󠉳󠉴󠉵󠉶󠉷󠉸󠉹󠉺󠉻󠉼󠉽󠉾󠉿󠊀󠊁󠊂󠊃󠊄󠊅󠊆󠊇󠊈󠊉󠊊󠊋󠊌󠊍󠊎󠊏󠊐󠊑󠊒󠊓󠊔󠊕󠊖󠊗󠊘󠊙󠊚󠊛󠊜󠊝󠊞󠊟󠊠󠊡󠊢󠊣󠊤󠊥󠊦󠊧󠊨󠊩󠊪󠊫󠊬󠊭󠊮󠊯󠊰󠊱󠊲󠊳󠊴󠊵󠊶󠊷󠊸󠊹󠊺󠊻󠊼󠊽󠊾󠊿󠋀󠋁󠋂󠋃󠋄󠋅󠋆󠋇󠋈󠋉󠋊󠋋󠋌󠋍󠋎󠋏󠋐󠋑󠋒󠋓󠋔󠋕󠋖󠋗󠋘󠋙󠋚󠋛󠋜󠋝󠋞󠋟󠋠󠋡󠋢󠋣󠋤󠋥󠋦󠋧󠋨󠋩󠋪󠋫󠋬󠋭󠋮󠋯󠋰󠋱󠋲󠋳󠋴󠋵󠋶󠋷󠋸󠋹󠋺󠋻󠋼󠋽󠋾󠋿󠌀󠌁󠌂󠌃󠌄󠌅󠌆󠌇󠌈󠌉󠌊󠌋󠌌󠌍󠌎󠌏󠌐󠌑󠌒󠌓󠌔󠌕󠌖󠌗󠌘󠌙󠌚󠌛󠌜󠌝󠌞󠌟󠌠󠌡󠌢󠌣󠌤󠌥󠌦󠌧󠌨󠌩󠌪󠌫󠌬󠌭󠌮󠌯󠌰󠌱󠌲󠌳󠌴󠌵󠌶󠌷󠌸󠌹󠌺󠌻󠌼󠌽󠌾󠌿󠍀󠍁󠍂󠍃󠍄󠍅󠍆󠍇󠍈󠍉󠍊󠍋󠍌󠍍󠍎󠍏󠍐󠍑󠍒󠍓󠍔󠍕󠍖󠍗󠍘󠍙󠍚󠍛󠍜󠍝󠍞󠍟󠍠󠍡󠍢󠍣󠍤󠍥󠍦󠍧󠍨󠍩󠍪󠍫󠍬󠍭󠍮󠍯󠍰󠍱󠍲󠍳󠍴󠍵󠍶󠍷󠍸󠍹󠍺󠍻󠍼󠍽󠍾󠍿󠎀󠎁󠎂󠎃󠎄󠎅󠎆󠎇󠎈󠎉󠎊󠎋󠎌󠎍󠎎󠎏󠎐󠎑󠎒󠎓󠎔󠎕󠎖󠎗󠎘󠎙󠎚󠎛󠎜󠎝󠎞󠎟󠎠󠎡󠎢󠎣󠎤󠎥󠎦󠎧󠎨󠎩󠎪󠎫󠎬󠎭󠎮󠎯󠎰󠎱󠎲󠎳󠎴󠎵󠎶󠎷󠎸󠎹󠎺󠎻󠎼󠎽󠎾󠎿󠏀󠏁󠏂󠏃󠏄󠏅󠏆󠏇󠏈󠏉󠏊󠏋󠏌󠏍󠏎󠏏󠏐󠏑󠏒󠏓󠏔󠏕󠏖󠏗󠏘󠏙󠏚󠏛󠏜󠏝󠏞󠏟󠏠󠏡󠏢󠏣󠏤󠏥󠏦󠏧󠏨󠏩󠏪󠏫󠏬󠏭󠏮󠏯󠏰󠏱󠏲󠏳󠏴󠏵󠏶󠏷󠏸󠏹󠏺󠏻󠏼󠏽󠏾󠏿󠐀󠐁󠐂󠐃󠐄󠐅󠐆󠐇󠐈󠐉󠐊󠐋󠐌󠐍󠐎󠐏󠐐󠐑󠐒󠐓󠐔󠐕󠐖󠐗󠐘󠐙󠐚󠐛󠐜󠐝󠐞󠐟󠐠󠐡󠐢󠐣󠐤󠐥󠐦󠐧󠐨󠐩󠐪󠐫󠐬󠐭󠐮󠐯󠐰󠐱󠐲󠐳󠐴󠐵󠐶󠐷󠐸󠐹󠐺󠐻󠐼󠐽󠐾󠐿󠑀󠑁󠑂󠑃󠑄󠑅󠑆󠑇󠑈󠑉󠑊󠑋󠑌󠑍󠑎󠑏󠑐󠑑󠑒󠑓󠑔󠑕󠑖󠑗󠑘󠑙󠑚󠑛󠑜󠑝󠑞󠑟󠑠󠑡󠑢󠑣󠑤󠑥󠑦󠑧󠑨󠑩󠑪󠑫󠑬󠑭󠑮󠑯󠑰󠑱󠑲󠑳󠑴󠑵󠑶󠑷󠑸󠑹󠑺󠑻󠑼󠑽󠑾󠑿󠒀󠒁󠒂󠒃󠒄󠒅󠒆󠒇󠒈󠒉󠒊󠒋󠒌󠒍󠒎󠒏󠒐󠒑󠒒󠒓󠒔󠒕󠒖󠒗󠒘󠒙󠒚󠒛󠒜󠒝󠒞󠒟󠒠󠒡󠒢󠒣󠒤󠒥󠒦󠒧󠒨󠒩󠒪󠒫󠒬󠒭󠒮󠒯󠒰󠒱󠒲󠒳󠒴󠒵󠒶󠒷󠒸󠒹󠒺󠒻󠒼󠒽󠒾󠒿󠓀󠓁󠓂󠓃󠓄󠓅󠓆󠓇󠓈󠓉󠓊󠓋󠓌󠓍󠓎󠓏󠓐󠓑󠓒󠓓󠓔󠓕󠓖󠓗󠓘󠓙󠓚󠓛󠓜󠓝󠓞󠓟󠓠󠓡󠓢󠓣󠓤󠓥󠓦󠓧󠓨󠓩󠓪󠓫󠓬󠓭󠓮󠓯󠓰󠓱󠓲󠓳󠓴󠓵󠓶󠓷󠓸󠓹󠓺󠓻󠓼󠓽󠓾󠓿󠔀󠔁󠔂󠔃󠔄󠔅󠔆󠔇󠔈󠔉󠔊󠔋󠔌󠔍󠔎󠔏󠔐󠔑󠔒󠔓󠔔󠔕󠔖󠔗󠔘󠔙󠔚󠔛󠔜󠔝󠔞󠔟󠔠󠔡󠔢󠔣󠔤󠔥󠔦󠔧󠔨󠔩󠔪󠔫󠔬󠔭󠔮󠔯󠔰󠔱󠔲󠔳󠔴󠔵󠔶󠔷󠔸󠔹󠔺󠔻󠔼󠔽󠔾󠔿󠕀󠕁󠕂󠕃󠕄󠕅󠕆󠕇󠕈󠕉󠕊󠕋󠕌󠕍󠕎󠕏󠕐󠕑󠕒󠕓󠕔󠕕󠕖󠕗󠕘󠕙󠕚󠕛󠕜󠕝󠕞󠕟󠕠󠕡󠕢󠕣󠕤󠕥󠕦󠕧󠕨󠕩󠕪󠕫󠕬󠕭󠕮󠕯󠕰󠕱󠕲󠕳󠕴󠕵󠕶󠕷󠕸󠕹󠕺󠕻󠕼󠕽󠕾󠕿󠖀󠖁󠖂󠖃󠖄󠖅󠖆󠖇󠖈󠖉󠖊󠖋󠖌󠖍󠖎󠖏󠖐󠖑󠖒󠖓󠖔󠖕󠖖󠖗󠖘󠖙󠖚󠖛󠖜󠖝󠖞󠖟󠖠󠖡󠖢󠖣󠖤󠖥󠖦󠖧󠖨󠖩󠖪󠖫󠖬󠖭󠖮󠖯󠖰󠖱󠖲󠖳󠖴󠖵󠖶󠖷󠖸󠖹󠖺󠖻󠖼󠖽󠖾󠖿󠗀󠗁󠗂󠗃󠗄󠗅󠗆󠗇󠗈󠗉󠗊󠗋󠗌󠗍󠗎󠗏󠗐󠗑󠗒󠗓󠗔󠗕󠗖󠗗󠗘󠗙󠗚󠗛󠗜󠗝󠗞󠗟󠗠󠗡󠗢󠗣󠗤󠗥󠗦󠗧󠗨󠗩󠗪󠗫󠗬󠗭󠗮󠗯󠗰󠗱󠗲󠗳󠗴󠗵󠗶󠗷󠗸󠗹󠗺󠗻󠗼󠗽󠗾󠗿󠘀󠘁󠘂󠘃󠘄󠘅󠘆󠘇󠘈󠘉󠘊󠘋󠘌󠘍󠘎󠘏󠘐󠘑󠘒󠘓󠘔󠘕󠘖󠘗󠘘󠘙󠘚󠘛󠘜󠘝󠘞󠘟󠘠󠘡󠘢󠘣󠘤󠘥󠘦󠘧󠘨󠘩󠘪󠘫󠘬󠘭󠘮󠘯󠘰󠘱󠘲󠘳󠘴󠘵󠘶󠘷󠘸󠘹󠘺󠘻󠘼󠘽󠘾󠘿󠙀󠙁󠙂󠙃󠙄󠙅󠙆󠙇󠙈󠙉󠙊󠙋󠙌󠙍󠙎󠙏󠙐󠙑󠙒󠙓󠙔󠙕󠙖󠙗󠙘󠙙󠙚󠙛󠙜󠙝󠙞󠙟󠙠󠙡󠙢󠙣󠙤󠙥󠙦󠙧󠙨󠙩󠙪󠙫󠙬󠙭󠙮󠙯󠙰󠙱󠙲󠙳󠙴󠙵󠙶󠙷󠙸󠙹󠙺󠙻󠙼󠙽󠙾󠙿󠚀󠚁󠚂󠚃󠚄󠚅󠚆󠚇󠚈󠚉󠚊󠚋󠚌󠚍󠚎󠚏󠚐󠚑󠚒󠚓󠚔󠚕󠚖󠚗󠚘󠚙󠚚󠚛󠚜󠚝󠚞󠚟󠚠󠚡󠚢󠚣󠚤󠚥󠚦󠚧󠚨󠚩󠚪󠚫󠚬󠚭󠚮󠚯󠚰󠚱󠚲󠚳󠚴󠚵󠚶󠚷󠚸󠚹󠚺󠚻󠚼󠚽󠚾󠚿󠛀󠛁󠛂󠛃󠛄󠛅󠛆󠛇󠛈󠛉󠛊󠛋󠛌󠛍󠛎󠛏󠛐󠛑󠛒󠛓󠛔󠛕󠛖󠛗󠛘󠛙󠛚󠛛󠛜󠛝󠛞󠛟󠛠󠛡󠛢󠛣󠛤󠛥󠛦󠛧󠛨󠛩󠛪󠛫󠛬󠛭󠛮󠛯󠛰󠛱󠛲󠛳󠛴󠛵󠛶󠛷󠛸󠛹󠛺󠛻󠛼󠛽󠛾󠛿󠜀󠜁󠜂󠜃󠜄󠜅󠜆󠜇󠜈󠜉󠜊󠜋󠜌󠜍󠜎󠜏󠜐󠜑󠜒󠜓󠜔󠜕󠜖󠜗󠜘󠜙󠜚󠜛󠜜󠜝󠜞󠜟󠜠󠜡󠜢󠜣󠜤󠜥󠜦󠜧󠜨󠜩󠜪󠜫󠜬󠜭󠜮󠜯󠜰󠜱󠜲󠜳󠜴󠜵󠜶󠜷󠜸󠜹󠜺󠜻󠜼󠜽󠜾󠜿󠝀󠝁󠝂󠝃󠝄󠝅󠝆󠝇󠝈󠝉󠝊󠝋󠝌󠝍󠝎󠝏󠝐󠝑󠝒󠝓󠝔󠝕󠝖󠝗󠝘󠝙󠝚󠝛󠝜󠝝󠝞󠝟󠝠󠝡󠝢󠝣󠝤󠝥󠝦󠝧󠝨󠝩󠝪󠝫󠝬󠝭󠝮󠝯󠝰󠝱󠝲󠝳󠝴󠝵󠝶󠝷󠝸󠝹󠝺󠝻󠝼󠝽󠝾󠝿󠞀󠞁󠞂󠞃󠞄󠞅󠞆󠞇󠞈󠞉󠞊󠞋󠞌󠞍󠞎󠞏󠞐󠞑󠞒󠞓󠞔󠞕󠞖󠞗󠞘󠞙󠞚󠞛󠞜󠞝󠞞󠞟󠞠󠞡󠞢󠞣󠞤󠞥󠞦󠞧󠞨󠞩󠞪󠞫󠞬󠞭󠞮󠞯󠞰󠞱󠞲󠞳󠞴󠞵󠞶󠞷󠞸󠞹󠞺󠞻󠞼󠞽󠞾󠞿󠟀󠟁󠟂󠟃󠟄󠟅󠟆󠟇󠟈󠟉󠟊󠟋󠟌󠟍󠟎󠟏󠟐󠟑󠟒󠟓󠟔󠟕󠟖󠟗󠟘󠟙󠟚󠟛󠟜󠟝󠟞󠟟󠟠󠟡󠟢󠟣󠟤󠟥󠟦󠟧󠟨󠟩󠟪󠟫󠟬󠟭󠟮󠟯󠟰󠟱󠟲󠟳󠟴󠟵󠟶󠟷󠟸󠟹󠟺󠟻󠟼󠟽󠟾󠟿󠠀󠠁󠠂󠠃󠠄󠠅󠠆󠠇󠠈󠠉󠠊󠠋󠠌󠠍󠠎󠠏󠠐󠠑󠠒󠠓󠠔󠠕󠠖󠠗󠠘󠠙󠠚󠠛󠠜󠠝󠠞󠠟󠠠󠠡󠠢󠠣󠠤󠠥󠠦󠠧󠠨󠠩󠠪󠠫󠠬󠠭󠠮󠠯󠠰󠠱󠠲󠠳󠠴󠠵󠠶󠠷󠠸󠠹󠠺󠠻󠠼󠠽󠠾󠠿󠡀󠡁󠡂󠡃󠡄󠡅󠡆󠡇󠡈󠡉󠡊󠡋󠡌󠡍󠡎󠡏󠡐󠡑󠡒󠡓󠡔󠡕󠡖󠡗󠡘󠡙󠡚󠡛󠡜󠡝󠡞󠡟󠡠󠡡󠡢󠡣󠡤󠡥󠡦󠡧󠡨󠡩󠡪󠡫󠡬󠡭󠡮󠡯󠡰󠡱󠡲󠡳󠡴󠡵󠡶󠡷󠡸󠡹󠡺󠡻󠡼󠡽󠡾󠡿󠢀󠢁󠢂󠢃󠢄󠢅󠢆󠢇󠢈󠢉󠢊󠢋󠢌󠢍󠢎󠢏󠢐󠢑󠢒󠢓󠢔󠢕󠢖󠢗󠢘󠢙󠢚󠢛󠢜󠢝󠢞󠢟󠢠󠢡󠢢󠢣󠢤󠢥󠢦󠢧󠢨󠢩󠢪󠢫󠢬󠢭󠢮󠢯󠢰󠢱󠢲󠢳󠢴󠢵󠢶󠢷󠢸󠢹󠢺󠢻󠢼󠢽󠢾󠢿󠣀󠣁󠣂󠣃󠣄󠣅󠣆󠣇󠣈󠣉󠣊󠣋󠣌󠣍󠣎󠣏󠣐󠣑󠣒󠣓󠣔󠣕󠣖󠣗󠣘󠣙󠣚󠣛󠣜󠣝󠣞󠣟󠣠󠣡󠣢󠣣󠣤󠣥󠣦󠣧󠣨󠣩󠣪󠣫󠣬󠣭󠣮󠣯󠣰󠣱󠣲󠣳󠣴󠣵󠣶󠣷󠣸󠣹󠣺󠣻󠣼󠣽󠣾󠣿󠤀󠤁󠤂󠤃󠤄󠤅󠤆󠤇󠤈󠤉󠤊󠤋󠤌󠤍󠤎󠤏󠤐󠤑󠤒󠤓󠤔󠤕󠤖󠤗󠤘󠤙󠤚󠤛󠤜󠤝󠤞󠤟󠤠󠤡󠤢󠤣󠤤󠤥󠤦󠤧󠤨󠤩󠤪󠤫󠤬󠤭󠤮󠤯󠤰󠤱󠤲󠤳󠤴󠤵󠤶󠤷󠤸󠤹󠤺󠤻󠤼󠤽󠤾󠤿󠥀󠥁󠥂󠥃󠥄󠥅󠥆󠥇󠥈󠥉󠥊󠥋󠥌󠥍󠥎󠥏󠥐󠥑󠥒󠥓󠥔󠥕󠥖󠥗󠥘󠥙󠥚󠥛󠥜󠥝󠥞󠥟󠥠󠥡󠥢󠥣󠥤󠥥󠥦󠥧󠥨󠥩󠥪󠥫󠥬󠥭󠥮󠥯󠥰󠥱󠥲󠥳󠥴󠥵󠥶󠥷󠥸󠥹󠥺󠥻󠥼󠥽󠥾󠥿󠦀󠦁󠦂󠦃󠦄󠦅󠦆󠦇󠦈󠦉󠦊󠦋󠦌󠦍󠦎󠦏󠦐󠦑󠦒󠦓󠦔󠦕󠦖󠦗󠦘󠦙󠦚󠦛󠦜󠦝󠦞󠦟󠦠󠦡󠦢󠦣󠦤󠦥󠦦󠦧󠦨󠦩󠦪󠦫󠦬󠦭󠦮󠦯󠦰󠦱󠦲󠦳󠦴󠦵󠦶󠦷󠦸󠦹󠦺󠦻󠦼󠦽󠦾󠦿󠧀󠧁󠧂󠧃󠧄󠧅󠧆󠧇󠧈󠧉󠧊󠧋󠧌󠧍󠧎󠧏󠧐󠧑󠧒󠧓󠧔󠧕󠧖󠧗󠧘󠧙󠧚󠧛󠧜󠧝󠧞󠧟󠧠󠧡󠧢󠧣󠧤󠧥󠧦󠧧󠧨󠧩󠧪󠧫󠧬󠧭󠧮󠧯󠧰󠧱󠧲󠧳󠧴󠧵󠧶󠧷󠧸󠧹󠧺󠧻󠧼󠧽󠧾󠧿󠨀󠨁󠨂󠨃󠨄󠨅󠨆󠨇󠨈󠨉󠨊󠨋󠨌󠨍󠨎󠨏󠨐󠨑󠨒󠨓󠨔󠨕󠨖󠨗󠨘󠨙󠨚󠨛󠨜󠨝󠨞󠨟󠨠󠨡󠨢󠨣󠨤󠨥󠨦󠨧󠨨󠨩󠨪󠨫󠨬󠨭󠨮󠨯󠨰󠨱󠨲󠨳󠨴󠨵󠨶󠨷󠨸󠨹󠨺󠨻󠨼󠨽󠨾󠨿󠩀󠩁󠩂󠩃󠩄󠩅󠩆󠩇󠩈󠩉󠩊󠩋󠩌󠩍󠩎󠩏󠩐󠩑󠩒󠩓󠩔󠩕󠩖󠩗󠩘󠩙󠩚󠩛󠩜󠩝󠩞󠩟󠩠󠩡󠩢󠩣󠩤󠩥󠩦󠩧󠩨󠩩󠩪󠩫󠩬󠩭󠩮󠩯󠩰󠩱󠩲󠩳󠩴󠩵󠩶󠩷󠩸󠩹󠩺󠩻󠩼󠩽󠩾󠩿󠪀󠪁󠪂󠪃󠪄󠪅󠪆󠪇󠪈󠪉󠪊󠪋󠪌󠪍󠪎󠪏󠪐󠪑󠪒󠪓󠪔󠪕󠪖󠪗󠪘󠪙󠪚󠪛󠪜󠪝󠪞󠪟󠪠󠪡󠪢󠪣󠪤󠪥󠪦󠪧󠪨󠪩󠪪󠪫󠪬󠪭󠪮󠪯󠪰󠪱󠪲󠪳󠪴󠪵󠪶󠪷󠪸󠪹󠪺󠪻󠪼󠪽󠪾󠪿󠫀󠫁󠫂󠫃󠫄󠫅󠫆󠫇󠫈󠫉󠫊󠫋󠫌󠫍󠫎󠫏󠫐󠫑󠫒󠫓󠫔󠫕󠫖󠫗󠫘󠫙󠫚󠫛󠫜󠫝󠫞󠫟󠫠󠫡󠫢󠫣󠫤󠫥󠫦󠫧󠫨󠫩󠫪󠫫󠫬󠫭󠫮󠫯󠫰󠫱󠫲󠫳󠫴󠫵󠫶󠫷󠫸󠫹󠫺󠫻󠫼󠫽󠫾󠫿󠬀󠬁󠬂󠬃󠬄󠬅󠬆󠬇󠬈󠬉󠬊󠬋󠬌󠬍󠬎󠬏󠬐󠬑󠬒󠬓󠬔󠬕󠬖󠬗󠬘󠬙󠬚󠬛󠬜󠬝󠬞󠬟󠬠󠬡󠬢󠬣󠬤󠬥󠬦󠬧󠬨󠬩󠬪󠬫󠬬󠬭󠬮󠬯󠬰󠬱󠬲󠬳󠬴󠬵󠬶󠬷󠬸󠬹󠬺󠬻󠬼󠬽󠬾󠬿󠭀󠭁󠭂󠭃󠭄󠭅󠭆󠭇󠭈󠭉󠭊󠭋󠭌󠭍󠭎󠭏󠭐󠭑󠭒󠭓󠭔󠭕󠭖󠭗󠭘󠭙󠭚󠭛󠭜󠭝󠭞󠭟󠭠󠭡󠭢󠭣󠭤󠭥󠭦󠭧󠭨󠭩󠭪󠭫󠭬󠭭󠭮󠭯󠭰󠭱󠭲󠭳󠭴󠭵󠭶󠭷󠭸󠭹󠭺󠭻󠭼󠭽󠭾󠭿󠮀󠮁󠮂󠮃󠮄󠮅󠮆󠮇󠮈󠮉󠮊󠮋󠮌󠮍󠮎󠮏󠮐󠮑󠮒󠮓󠮔󠮕󠮖󠮗󠮘󠮙󠮚󠮛󠮜󠮝󠮞󠮟󠮠󠮡󠮢󠮣󠮤󠮥󠮦󠮧󠮨󠮩󠮪󠮫󠮬󠮭󠮮󠮯󠮰󠮱󠮲󠮳󠮴󠮵󠮶󠮷󠮸󠮹󠮺󠮻󠮼󠮽󠮾󠮿󠯀󠯁󠯂󠯃󠯄󠯅󠯆󠯇󠯈󠯉󠯊󠯋󠯌󠯍󠯎󠯏󠯐󠯑󠯒󠯓󠯔󠯕󠯖󠯗󠯘󠯙󠯚󠯛󠯜󠯝󠯞󠯟󠯠󠯡󠯢󠯣󠯤󠯥󠯦󠯧󠯨󠯩󠯪󠯫󠯬󠯭󠯮󠯯󠯰󠯱󠯲󠯳󠯴󠯵󠯶󠯷󠯸󠯹󠯺󠯻󠯼󠯽󠯾󠯿󠰀󠰁󠰂󠰃󠰄󠰅󠰆󠰇󠰈󠰉󠰊󠰋󠰌󠰍󠰎󠰏󠰐󠰑󠰒󠰓󠰔󠰕󠰖󠰗󠰘󠰙󠰚󠰛󠰜󠰝󠰞󠰟󠰠󠰡󠰢󠰣󠰤󠰥󠰦󠰧󠰨󠰩󠰪󠰫󠰬󠰭󠰮󠰯󠰰󠰱󠰲󠰳󠰴󠰵󠰶󠰷󠰸󠰹󠰺󠰻󠰼󠰽󠰾󠰿󠱀󠱁󠱂󠱃󠱄󠱅󠱆󠱇󠱈󠱉󠱊󠱋󠱌󠱍󠱎󠱏󠱐󠱑󠱒󠱓󠱔󠱕󠱖󠱗󠱘󠱙󠱚󠱛󠱜󠱝󠱞󠱟󠱠󠱡󠱢󠱣󠱤󠱥󠱦󠱧󠱨󠱩󠱪󠱫󠱬󠱭󠱮󠱯󠱰󠱱󠱲󠱳󠱴󠱵󠱶󠱷󠱸󠱹󠱺󠱻󠱼󠱽󠱾󠱿󠲀󠲁󠲂󠲃󠲄󠲅󠲆󠲇󠲈󠲉󠲊󠲋󠲌󠲍󠲎󠲏󠲐󠲑󠲒󠲓󠲔󠲕󠲖󠲗󠲘󠲙󠲚󠲛󠲜󠲝󠲞󠲟󠲠󠲡󠲢󠲣󠲤󠲥󠲦󠲧󠲨󠲩󠲪󠲫󠲬󠲭󠲮󠲯󠲰󠲱󠲲󠲳󠲴󠲵󠲶󠲷󠲸󠲹󠲺󠲻󠲼󠲽󠲾󠲿󠳀󠳁󠳂󠳃󠳄󠳅󠳆󠳇󠳈󠳉󠳊󠳋󠳌󠳍󠳎󠳏󠳐󠳑󠳒󠳓󠳔󠳕󠳖󠳗󠳘󠳙󠳚󠳛󠳜󠳝󠳞󠳟󠳠󠳡󠳢󠳣󠳤󠳥󠳦󠳧󠳨󠳩󠳪󠳫󠳬󠳭󠳮󠳯󠳰󠳱󠳲󠳳󠳴󠳵󠳶󠳷󠳸󠳹󠳺󠳻󠳼󠳽󠳾󠳿󠴀󠴁󠴂󠴃󠴄󠴅󠴆󠴇󠴈󠴉󠴊󠴋󠴌󠴍󠴎󠴏󠴐󠴑󠴒󠴓󠴔󠴕󠴖󠴗󠴘󠴙󠴚󠴛󠴜󠴝󠴞󠴟󠴠󠴡󠴢󠴣󠴤󠴥󠴦󠴧󠴨󠴩󠴪󠴫󠴬󠴭󠴮󠴯󠴰󠴱󠴲󠴳󠴴󠴵󠴶󠴷󠴸󠴹󠴺󠴻󠴼󠴽󠴾󠴿󠵀󠵁󠵂󠵃󠵄󠵅󠵆󠵇󠵈󠵉󠵊󠵋󠵌󠵍󠵎󠵏󠵐󠵑󠵒󠵓󠵔󠵕󠵖󠵗󠵘󠵙󠵚󠵛󠵜󠵝󠵞󠵟󠵠󠵡󠵢󠵣󠵤󠵥󠵦󠵧󠵨󠵩󠵪󠵫󠵬󠵭󠵮󠵯󠵰󠵱󠵲󠵳󠵴󠵵󠵶󠵷󠵸󠵹󠵺󠵻󠵼󠵽󠵾󠵿󠶀󠶁󠶂󠶃󠶄󠶅󠶆󠶇󠶈󠶉󠶊󠶋󠶌󠶍󠶎󠶏󠶐󠶑󠶒󠶓󠶔󠶕󠶖󠶗󠶘󠶙󠶚󠶛󠶜󠶝󠶞󠶟󠶠󠶡󠶢󠶣󠶤󠶥󠶦󠶧󠶨󠶩󠶪󠶫󠶬󠶭󠶮󠶯󠶰󠶱󠶲󠶳󠶴󠶵󠶶󠶷󠶸󠶹󠶺󠶻󠶼󠶽󠶾󠶿󠷀󠷁󠷂󠷃󠷄󠷅󠷆󠷇󠷈󠷉󠷊󠷋󠷌󠷍󠷎󠷏󠷐󠷑󠷒󠷓󠷔󠷕󠷖󠷗󠷘󠷙󠷚󠷛󠷜󠷝󠷞󠷟󠷠󠷡󠷢󠷣󠷤󠷥󠷦󠷧󠷨󠷩󠷪󠷫󠷬󠷭󠷮󠷯󠷰󠷱󠷲󠷳󠷴󠷵󠷶󠷷󠷸󠷹󠷺󠷻󠷼󠷽󠷾󠷿󠸀󠸁󠸂󠸃󠸄󠸅󠸆󠸇󠸈󠸉󠸊󠸋󠸌󠸍󠸎󠸏󠸐󠸑󠸒󠸓󠸔󠸕󠸖󠸗󠸘󠸙󠸚󠸛󠸜󠸝󠸞󠸟󠸠󠸡󠸢󠸣󠸤󠸥󠸦󠸧󠸨󠸩󠸪󠸫󠸬󠸭󠸮󠸯󠸰󠸱󠸲󠸳󠸴󠸵󠸶󠸷󠸸󠸹󠸺󠸻󠸼󠸽󠸾󠸿󠹀󠹁󠹂󠹃󠹄󠹅󠹆󠹇󠹈󠹉󠹊󠹋󠹌󠹍󠹎󠹏󠹐󠹑󠹒󠹓󠹔󠹕󠹖󠹗󠹘󠹙󠹚󠹛󠹜󠹝󠹞󠹟󠹠󠹡󠹢󠹣󠹤󠹥󠹦󠹧󠹨󠹩󠹪󠹫󠹬󠹭󠹮󠹯󠹰󠹱󠹲󠹳󠹴󠹵󠹶󠹷󠹸󠹹󠹺󠹻󠹼󠹽󠹾󠹿󠺀󠺁󠺂󠺃󠺄󠺅󠺆󠺇󠺈󠺉󠺊󠺋󠺌󠺍󠺎󠺏󠺐󠺑󠺒󠺓󠺔󠺕󠺖󠺗󠺘󠺙󠺚󠺛󠺜󠺝󠺞󠺟󠺠󠺡󠺢󠺣󠺤󠺥󠺦󠺧󠺨󠺩󠺪󠺫󠺬󠺭󠺮󠺯󠺰󠺱󠺲󠺳󠺴󠺵󠺶󠺷󠺸󠺹󠺺󠺻󠺼󠺽󠺾󠺿󠻀󠻁󠻂󠻃󠻄󠻅󠻆󠻇󠻈󠻉󠻊󠻋󠻌󠻍󠻎󠻏󠻐󠻑󠻒󠻓󠻔󠻕󠻖󠻗󠻘󠻙󠻚󠻛󠻜󠻝󠻞󠻟󠻠󠻡󠻢󠻣󠻤󠻥󠻦󠻧󠻨󠻩󠻪󠻫󠻬󠻭󠻮󠻯󠻰󠻱󠻲󠻳󠻴󠻵󠻶󠻷󠻸󠻹󠻺󠻻󠻼󠻽󠻾󠻿󠼀󠼁󠼂󠼃󠼄󠼅󠼆󠼇󠼈󠼉󠼊󠼋󠼌󠼍󠼎󠼏󠼐󠼑󠼒󠼓󠼔󠼕󠼖󠼗󠼘󠼙󠼚󠼛󠼜󠼝󠼞󠼟󠼠󠼡󠼢󠼣󠼤󠼥󠼦󠼧󠼨󠼩󠼪󠼫󠼬󠼭󠼮󠼯󠼰󠼱󠼲󠼳󠼴󠼵󠼶󠼷󠼸󠼹󠼺󠼻󠼼󠼽󠼾󠼿󠽀󠽁󠽂󠽃󠽄󠽅󠽆󠽇󠽈󠽉󠽊󠽋󠽌󠽍󠽎󠽏󠽐󠽑󠽒󠽓󠽔󠽕󠽖󠽗󠽘󠽙󠽚󠽛󠽜󠽝󠽞󠽟󠽠󠽡󠽢󠽣󠽤󠽥󠽦󠽧󠽨󠽩󠽪󠽫󠽬󠽭󠽮󠽯󠽰󠽱󠽲󠽳󠽴󠽵󠽶󠽷󠽸󠽹󠽺󠽻󠽼󠽽󠽾󠽿󠾀󠾁󠾂󠾃󠾄󠾅󠾆󠾇󠾈󠾉󠾊󠾋󠾌󠾍󠾎󠾏󠾐󠾑󠾒󠾓󠾔󠾕󠾖󠾗󠾘󠾙󠾚󠾛󠾜󠾝󠾞󠾟󠾠󠾡󠾢󠾣󠾤󠾥󠾦󠾧󠾨󠾩󠾪󠾫󠾬󠾭󠾮󠾯󠾰󠾱󠾲󠾳󠾴󠾵󠾶󠾷󠾸󠾹󠾺󠾻󠾼󠾽󠾾󠾿󠿀󠿁󠿂󠿃󠿄󠿅󠿆󠿇󠿈󠿉󠿊󠿋󠿌󠿍󠿎󠿏󠿐󠿑󠿒󠿓󠿔󠿕󠿖󠿗󠿘󠿙󠿚󠿛󠿜󠿝󠿞󠿟󠿠󠿡󠿢󠿣󠿤󠿥󠿦󠿧󠿨󠿩󠿪󠿫󠿬󠿭󠿮󠿯󠿰󠿱󠿲󠿳󠿴󠿵󠿶󠿷󠿸󠿹󠿺󠿻󠿼󠿽󠿾󠿿')
def unquote(s: str, /) -> str:
    """Conditional percent decoding."""
    decoder = IncrementalDecoder("ignore")
    bs = s.encode().split(b"%")
    out = decoder.decode(bs[0])
    for i, part in enumerate(bs[1:], start=1):
        final = i == len(bs)-1
        try:
            n = int(part[:2], 16)
        except ValueError:
            out += decoder.decode(b"%" + part, final=final)
            continue
        t = decoder.decode(bytes([n]))
        out += "".join([f"%{x:02X}" for x in t.encode()]) if t and t not in SAFE else t
        out += decoder.decode(part[2:], final=final)
    return out

def url_to_text(url: URL, /) -> str:
    """Convert a WHATWG URL to a string."""
    if url.origin == "null" and url.pathname.startswith("//"):
        s = url.protocol
    else:
        t = "".join([url.username, *[":", url.password]*bool(url.password), "@"]*bool(url.username))
        s = f"{url.protocol}//{t}{url.host}"
    return f"{s}{unquote(url.pathname)}{unquote(url.search)}{unquote(url.hash)}"

bad_whitespace_regex = regex.compile(r"""
\p{Cf}|\p{Zl}|\p{Zp}|[^\P{Cc}\n]|[^\P{Zs}\ ]
|\N{COMBINING GRAPHEME JOINER}|\N{KHMER VOWEL INHERENT AQ}|\N{KHMER VOWEL INHERENT AA}
|\N{HANGUL JUNGSEONG FILLER}|\N{HANGUL FILLER}|\N{HALFWIDTH HANGUL FILLER}
""", regex.VERBOSE)

def clean_whitespace(s: str, /) -> str:
    """Remove "special" whitespace characters from a string."""
    return bad_whitespace_regex.sub("", s)

confusables = {
    "h": ["H", "һ", "հ", "Ꮒ", "ℎ", "𝐡", "𝒉", "𝒽", "𝓱", "𝔥", "𝕙", "𝖍", "𝗁", "𝗵", "𝘩", "𝙝", "𝚑", "ｈ"],
    "t": ["T", "𝐭", "𝑡", "𝒕", "𝓉", "𝓽", "𝔱", "𝕥", "𝖙", "𝗍", "𝘁", "𝘵", "𝙩", "𝚝"],
    "p": ["P", "ρ", "ϱ", "р", "⍴", "ⲣ", "𝐩", "𝑝", "𝒑", "𝓅", "𝓹", "𝔭", "𝕡", "𝖕", "𝗉", "𝗽", "𝘱", "𝙥", "𝚙", "𝛒", "𝛠", "𝜌", "𝜚", "𝝆", "𝝔", "𝞀", "𝞎", "𝞺", "𝟈", "ｐ", "ҏ"],
    "s": ["S", "ƽ", "ѕ", "ꜱ", "ꮪ", "𐑈", "𑣁", "𝐬", "𝑠", "𝒔", "𝓈", "𝓼", "𝔰", "𝕤", "𝖘", "𝗌", "𝘀", "𝘴", "𝙨", "𝚜", "ｓ"],
    ":": ["ː", "˸", "։", "׃", "܃", "܄", "\N{DEVANAGARI SIGN VISARGA}", "\N{GUJARATI SIGN VISARGA}", "᛬", "᠃", "᠉", "⁚", "∶", "ꓽ", "꞉", "︰", "：", ";", ";"],
    "/": ["᜵", "⁁", "⁄", "∕", "╱", "⟋", "⧸", "Ⳇ", "⼃", "〳", "ノ", "㇓", "丿", "𝈺"],
}
confusable_table = {ord(v): k for k, vs in confusables.items() for v in vs}

def clean_scheme_confusables(s: str, /) -> str:
    """Replace confusable characters found in HTTP(S) URL schemes with the ASCII equivalents."""
    return s.translate(confusable_table)

def has_special_link(s: str, /) -> bool:
    """Determine if a string contains "special links" such as discord.gg invites.

    Special logic is used in Discord to detect these links. As such, they do not need to match the usual URL pattern
    to be prevented from appearing in the text part of a link. An example of this is that [discord.gg/abcd](https://a)
    is not accepted as a link, despite the URL lacking a scheme.
    """
    # TODO: fix stub
    return False

def _is_link_admissable(m: Markup, /, *, allow_emoji: bool) -> bool | None:
    allowed = [Text, Underline, Bold, Italic, Strikethrough, InlineCode, Spoiler, Timestamp, List, Header, Subtext, Quote]
    if allow_emoji:
        allowed += [UnicodeEmoji, CustomEmoji]

    # we can't use {meth}`walk` because the AST walk Discord does for their equivalent of this function
    # fails to go into lists. whoops!
    has_text = False
    for node in m.nodes:
        if type(node) == Style:
            # the type being exactly Style means that this is a dummy node representing
            # an inline code block, so force-allow emoji when recursing
            r = _is_link_admissable(node.inner, allow_emoji=True)
        elif type(node) not in allowed:
            return None
        else:
            match node:
                case Style(b):
                    r = _is_link_admissable(b, allow_emoji=allow_emoji)
                case Text(t):
                    r = not t.isspace()
                case _:
                    r = True
        if r is None:
            return None
        has_text = has_text or r

    return has_text

def is_link_admissable(ctx: Context, s: str, /, *, allow_emoji: bool) -> bool | None:
    """Determine if a string is allowed to be included in a [text](url) link.

    Discord contains rudimentary "phishing prevention" designed to prevent the creation of malicious links that
    pretend to be a different link than they are, e.g. [https://google.com](https://malicioussite.info).
    This is done by parsing the body and title of the link to see if they contain "unapproved" AST nodes,
    which is the responsibility of this function.

    The result is either None, indicating the link is not admissable, or a boolean indicating whether
    or not the tree contains any non-whitespace characters when rendered.
    """
    if has_special_link(s):
        return None

    return _is_link_admissable(ctx.parse(clean_scheme_confusables(clean_whitespace(s))), allow_emoji=allow_emoji)
