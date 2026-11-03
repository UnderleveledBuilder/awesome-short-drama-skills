# xindoo/sumeru · 第 3 次运行

- 仓库：https://github.com/xindoo/sumeru/tree/ac32d4a5d68bb30583f34867cb972da415e6badc
- 安装的 skill：sumeru-deconstruct、sumeru-finalize、sumeru-outline、sumeru-polish、sumeru-review、sumeru-topic、sumeru-worldbuilder、sumeru-write
- 环境：2.1.314 (Claude Code)，模型 claude-opus-5-5，推理强度 high
- 开始：2026-10-30T17:37:29-07:00，结束：2026-10-30T17:42:33-07:00
- 轮数：4，总耗时 5 分钟，按 API 价格折算 $4.05

## 第 1 轮

**用户：**

/sumeru-outline 我要给一部短剧写全剧骨架，要求在 premise.md 里，写好存成文件放在当前目录。

**工具调用：**Bash×5、Edit×2、Write×1

**Agent 最后的回复：**

I've written the full-series skeleton and saved it in the current directory as `验尸官的婚礼_全剧骨架.md`. Counted the way Word counts Chinese text, it's about 2,970 字, so it's under the 3,000-字 limit. It's skeleton only, as the premise asks: no episode-by-episode outline and no script text.

**What it contains:**
1. **Story engine:** a per-episode formula (pick up the last hook, one round of attack and defense, end on a hook you can see) plus three hard rules. The most important rule: we never clear 林晚 of signing the false report. She has to face it herself.
2. **Backstory bible:** the full timeline from four years ago to now. It fills the gaps in the premise:
   - why she didn't recognize 沈峥's body at the time;
   - why the double broke off the engagement as soon as he came back;
   - how 宋知远 uses 程野's sister as leverage;
   - where the anchor cufflink went.
3. **Reveal order:** locked at nine points (episodes 1, 15, 20, 30, 40, 45, 52, 59), so later writers can't give away the truth early. The audience learns the killer at episode 30; 林晚 learns it at episode 45.
4. **Character arcs:** turning-point episodes for all seven main characters.
5. **Five acts:** 婚礼 (1–10), 切片 (11–20), 替身 (21–40), 签名 (41–52) and 重写 (53–60). Paywall cliffhangers fall at episodes 10, 20, 30, 40 and 50; the two biggest climaxes are episode 40 and episode 59.
6. **Evidence ledger:** each piece of evidence, how the 沈 family tries to destroy it, and whose face it slaps. At episode 34 林晚 genuinely loses, and the original slice is destroyed.
7. **Setups and payoffs, AI-shooting limits, and no-go rules:**
   - each character keeps a fixed visual marker all series;
   - the main settings are capped at 9;
   - no underwater shots, fight scenes or big crowd scenes.

**Things I added that aren't in the premise. Please check these:**
- The scar on 沈峥's hand came from shielding 林晚 from a knife.
- The watch lid is engraved "林法医，早点下班。", revealed only in episode 60.
- 程野's sister is named 程禾.
- 宋知远's two cufflinks don't match: one is newer, because the dead man was clutching the other.
- 沈砚 woke up that night with blood on his hands and has suspected himself ever since.
- The deadline is 沈峥's 30th-birthday share handover in episode 40.

All character names come from your premise, and none of them match the skill's naming blocklist. Since you only asked for a skeleton, I skipped the novel-style files the skill normally produces, such as the chapter outlines and the `.sumeru/` JSON data. I can add them if you want them later.

## 第 2 轮

**用户：**

如果要我在几个方案里选，就选你最推荐的那个；其他要我定的，都按你推荐的来，不用再问我。请继续，直到 premise.md 要的全剧骨架写成文件；骨架之后的分集大纲和剧本不用写。

**工具调用：**Bash×1、Edit×6、Read×1

**Agent 最后的回复：**

I've finished the full-series skeleton and saved it in the current directory as `验尸官的婚礼_全剧骨架.md`. It's about 2,990 字 counted the way Word counts Chinese text, so it's under the 3,000-字 limit. It has no episode outlines and no script text.

On a final read I found three logic problems and fixed them:
1. **Episode 1:** the groom took his glove off, which contradicts the premise ("婚礼上一直戴着白手套") and the episode-40 moment when he takes it off in public. Now red wine spills on his left hand during the toast, he pulls the glove off for a few seconds to wipe it, then puts it back on. That's when 林晚 sees there's no scar.
2. **Episode 10:** 苏曼丽 slipped 林晚 her SOS room card, but 苏曼丽 wasn't in the room. Now 苏曼丽 is there first and says her husband won't take his gloves off even to sleep, and that she's scared. Then 程野 walks in and begs for help for his sister.
3. **Reveal order:** in episode 1, 林晚 now only suspects the unidentified body from three years ago was 沈峥. It's proven by DNA in episode 20.

Everything you would have had to decide, I settled with my recommended option. The main additions I made beyond the premise are still in the file:
- the knife-wound origin of 沈峥's scar;
- the watch engraving "林法医，早点下班。";
- the sister's name, 程禾;
- 宋知远's mismatched cufflinks;
- 沈砚 waking up with blood on his hands;
- the share-handover deadline in episode 40.

The skeleton is ready to be used to control the episode outlines and scripts.

## 第 3 轮

**用户：**

如果要我在几个方案里选，就选你最推荐的那个；其他要我定的，都按你推荐的来，不用再问我。请继续，直到 premise.md 要的全剧骨架写成文件；骨架之后的分集大纲和剧本不用写。

**工具调用：**Bash×1

**Agent 最后的回复：**

全剧骨架上一轮就已经写完了，这一轮我只确认了一下文件还在：`验尸官的婚礼_全剧骨架.md` 在当前目录里，约 2990 字，没超过 3000 字的上限。premise.md 要的骨架已经齐了，所以这次没有再改。

骨架共八部分：
1. 发动机：每集的固定写法和三条铁律
2. 真相底牌：完整时间线，以及锁死的揭示顺序
3. 七个主要人物的弧线和转折集数
4. 五段结构，覆盖第 1–60 集
5. 证据台账
6. 伏笔回收
7. AI 拍摄约束
8. 禁区

分集大纲和剧本按你的要求没有写。需要你定的地方，我都按自己最推荐的方案定了。

## 第 4 轮

**用户：**

如果要我在几个方案里选，就选你最推荐的那个；其他要我定的，都按你推荐的来，不用再问我。请继续，直到 premise.md 要的全剧骨架写成文件；骨架之后的分集大纲和剧本不用写。

**工具调用：**无

**Agent 最后的回复：**

骨架已经写完了，这一轮我没有再改。当前目录里的 `验尸官的婚礼_全剧骨架.md` 就是 premise.md 要的全剧骨架，约 2990 字，没超过 3000 字的上限。premise.md 的要求都已覆盖：

- **60 集怎么走**：分五段，第 10、20、30、40、50 集是卡点，第 40 集和第 59 集是两个最大的高潮。
- **证据线和签名线两条主线**：每集拿出一件看得见的证据，一直推到第 59 集，林晚当庭推翻自己三年前签的报告。
- **结局**：按 premise 原样落地，最后一场她把表放在沈峥墓前。
- **管住后面的分集和剧本**：锁死了真相揭示顺序，加上证据台账、伏笔回收表、AI 拍摄约束和禁区。

需要你拍板的地方，我都按自己最推荐的方案定了。分集大纲和剧本按要求没有写。
