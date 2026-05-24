# -*- coding: utf-8 -*-
"""
主线剧情配置 - 第1-10日
"""

STORY_DATA = {
    "days": [
        {
            "day": 1,
            "title": "降临",
            "default_scene": "interview_start",
            "scenes": [
                {
                    "scene_id": "interview_start",
                    "title": "面试房间",
                    "npcs": ["面试官"],
                    "text": "你猛然睁开眼，发现自己躺在一个陌生的房间里。\n四周是灰白色的墙壁，头顶的日光灯发出嗡嗡的声响。\n\n一个身穿黑色西装的男人坐在你对面，他的脸模糊不清。\n\n「欢迎来到终焉之地。」他的声音没有温度，「在这里，你将通过学习获得力量。答对题目，收集道。」\n\n「答错……」他顿了顿，「你不会想知道的。」\n\n他从桌上拿起一张卡片：「现在，选择你的初始生肖守护者。」",
                    "choices": [
                        {
                            "choice_id": "select_rat",
                            "text": "选择鼠",
                            "next_scene": "zodiac_selected_rat",
                            "effects": {
                                "flags": {"initial_zodiac": "rat"},
                                "faction_reputation": {"shadow": 5}
                            }
                        },
                        {
                            "choice_id": "select_dragon",
                            "text": "选择龙",
                            "next_scene": "zodiac_selected_dragon",
                            "effects": {
                                "flags": {"initial_zodiac": "dragon"},
                                "faction_reputation": {"fortune": 5}
                            }
                        },
                        {
                            "choice_id": "select_tiger",
                            "text": "选择虎",
                            "next_scene": "zodiac_selected_tiger",
                            "effects": {
                                "flags": {"initial_zodiac": "tiger"},
                                "faction_reputation": {"extremist": 5}
                            }
                        },
                        {
                            "choice_id": "select_horse",
                            "text": "选择马",
                            "next_scene": "zodiac_selected_horse",
                            "effects": {
                                "flags": {"initial_zodiac": "horse"},
                                "faction_reputation": {"heaven_gate": 5}
                            }
                        }
                    ]
                },
                {
                    "scene_id": "zodiac_selected_rat",
                    "title": "鼠之契约",
                    "text": "你伸手触碰卡片，一阵光芒涌入体内。\n\n「人级·智慧之鼠。」面试官宣布，「这是你最初的守护者。」\n\n卡片化为一只闪烁的金色小鼠，盘旋在你肩头。\n\n「从这里开始，向知识之城进发吧。」",
                    "next_scene": "day1_end",
                    "effects": {
                        "add_quest": "day1_first_battle",
                        "memory_fragment": {"type": "choice", "content": "选择了鼠作为初始生肖"}
                    }
                },
                {
                    "scene_id": "zodiac_selected_dragon",
                    "title": "龙之契约",
                    "text": "你伸手触碰卡片，空气中传来低沉的龙吟。\n\n「人级·全面之龙。」面试官宣布，「这是你最初的守护者。」\n\n卡片化为一条闪烁的金色小龙，缠绕在你手臂上。\n\n「从这里开始，向知识之城进发吧。」",
                    "next_scene": "day1_end",
                    "effects": {
                        "add_quest": "day1_first_battle",
                        "memory_fragment": {"type": "choice", "content": "选择了龙作为初始生肖"}
                    }
                },
                {
                    "scene_id": "zodiac_selected_tiger",
                    "title": "虎之契约",
                    "text": "你伸手触碰卡片，空气中弥漫着野性的气息。\n\n「人级·威猛之虎。」面试官宣布，「这是你最初的守护者。」\n\n卡片化为一只闪烁的金色猛虎，蹲伏在你身前。\n\n「从这里开始，向知识之城进发吧。」",
                    "next_scene": "day1_end",
                    "effects": {
                        "add_quest": "day1_first_battle",
                        "memory_fragment": {"type": "choice", "content": "选择了虎作为初始生肖"}
                    }
                },
                {
                    "scene_id": "zodiac_selected_horse",
                    "title": "马之契约",
                    "text": "你伸手触碰卡片，风声在耳边呼啸。\n\n「人级·速度之马。」面试官宣布，「这是你最初的守护者。」\n\n卡片化为一只闪烁的金色奔马，在你身侧飞驰。\n\n「从这里开始，向知识之城进发吧。」",
                    "next_scene": "day1_end",
                    "effects": {
                        "add_quest": "day1_first_battle",
                        "memory_fragment": {"type": "choice", "content": "选择了马作为初始生肖"}
                    }
                },
                {
                    "scene_id": "day1_end",
                    "title": "第一日结束",
                    "text": "面试官挥了挥手，房间的门缓缓打开。\n\n「明天开始你的学习之旅吧。」他说，「记住，终焉之地的规则只有一条——」\n\n「活下去，变得更强。」\n\n【第1日结束】",
                    "auto_advance": False
                }
            ]
        },
        {
            "day": 2,
            "title": "初试",
            "default_scene": "knowledge_city_entrance",
            "scenes": [
                {
                    "scene_id": "knowledge_city_entrance",
                    "title": "知识城池",
                    "text": "第二天清晨，你来到了一座巨大的城池前。\n\n城墙上刻满了文字，城门上方写着三个大字——「道城」。\n\n城门口站着几个觉醒者，他们看到你纷纷投来警惕的目光。\n\n一个红发青年靠在墙边，对你咧嘴一笑：「新来的？人级生肖在城里的挑战区。」",
                    "choices": [
                        {
                            "choice_id": "ask_info",
                            "text": "询问更多信息",
                            "next_scene": "red_hair_talk",
                            "effects": {"memory_fragment": {"type": "dialogue", "content": "与红发青年的对话"}}
                        },
                        {
                            "choice_id": "go_directly",
                            "text": "自己去看看",
                            "next_scene": "challenge_area",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "red_hair_talk",
                    "title": "乔家劲的忠告",
                    "text": "红发青年耸耸肩：「叫我乔家劲就行。」\n\n「这里的生肖分三等：人、地、天。想升级就得一个个挑战。」\n\n「不过……」他压低声音，「别只顾着战斗。这地方有几个势力——天堂口、极道、貔貅，还有藏在暗处的猫。」\n\n「选势力要慎重，选错了可没好果子吃。」",
                    "choices": [
                        {
                            "choice_id": "join_his_team",
                            "text": "询问他的势力",
                            "next_scene": "jo_join_team",
                            "effects": {"faction_reputation": {"heaven_gate": 5}}
                        },
                        {
                            "choice_id": "go_challenge",
                            "text": "去挑战区",
                            "next_scene": "challenge_area",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "jo_join_team",
                    "title": "乔家劲的邀请",
                    "text": "「我是天堂口的。」乔家劲拍拍胸口，「楚天秋大哥领导的。」\n\n「如果你想变强又不想孤军奋战，天堂口是个好选择。」\n\n「当然，最终还是你自己决定。」\n\n他递给你一块小令牌：「想清楚了来中央广场找我。」",
                    "next_scene": "challenge_area",
                    "effects": {
                        "flags": {"met_jojiajin": True},
                        "inventory": ["天堂口令牌"]
                    }
                },
                {
                    "scene_id": "challenge_area",
                    "title": "挑战区",
                    "text": "挑战区是一片开阔的广场，四周分布着十二道门。\n\n每道门上都刻着一个生肖图案，散发出不同颜色的光芒。\n\n人级区域的门呈青铜色，已经有几个觉醒者在排队。\n\n你注意到门上的提示：「挑战人级生肖：答对全部题目即可获得道」",
                    "choices": [
                        {
                            "choice_id": "challenge_rat",
                            "text": "挑战人鼠",
                            "next_scene": "battle_rat",
                            "effects": {}
                        },
                        {
                            "choice_id": "challenge_ox",
                            "text": "挑战人牛",
                            "next_scene": "battle_ox",
                            "effects": {}
                        },
                        {
                            "choice_id": "observe_first",
                            "text": "先观察别人挑战",
                            "next_scene": "observe_challenge",
                            "effects": {"flags": {"observed_challenge": True}}
                        }
                    ]
                },
                {
                    "scene_id": "observe_challenge",
                    "title": "观察挑战",
                    "text": "你退到一旁，观察其他觉醒者挑战。\n\n一个瘦高的男人走进了人蛇门，片刻后传来懊恼的喊声——\n\n「该死！又错了！」\n\n他踉跄着走出来，脸色苍白，看到你后苦笑道：「别像我一样大意。题目可不简单。」",
                    "next_scene": "challenge_area",
                    "effects": {
                        "flags": {"learned_observation": True},
                        "memory_fragment": {"type": "discovery", "content": "观察到挑战失败的案例"}
                    }
                },
                {
                    "scene_id": "battle_rat",
                    "title": "人鼠挑战",
                    "text": "你推开人鼠门，进入一片纯白的空间。\n\n一只巨大的金色小鼠出现在你面前，闪烁着智慧的光芒。\n\n「挑战者。」它开口，声音如银铃，「答对我三道题，道就是你的。」\n\n「答错……你将失去今天的挑战机会。」",
                    "choices": [
                        {
                            "choice_id": "start_battle",
                            "text": "开始战斗",
                            "next_scene": "battle_rat_start",
                            "effects": {"flags": {"in_battle": True, "current_battle": "rat"}}
                        },
                        {
                            "choice_id": "retreat",
                            "text": "再准备一下",
                            "next_scene": "challenge_area",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "battle_rat_start",
                    "title": "战斗开始",
                    "text": "【战斗系统启动】\n\n人鼠发出三道题目...\n\n(此处将调用RAG引擎生成题目)",
                    "auto_advance": True
                },
                {
                    "scene_id": "battle_ox",
                    "title": "人牛挑战",
                    "text": "你推开人牛门，进入一片金色的空间。\n\n一头巨大的金色牛出现在你面前，气势如山。\n\n「挑战者。」它沉声道，「展现你的力量吧。」",
                    "choices": [
                        {
                            "choice_id": "start_battle",
                            "text": "开始战斗",
                            "next_scene": "battle_ox_start",
                            "effects": {"flags": {"in_battle": True, "current_battle": "ox"}}
                        },
                        {
                            "choice_id": "retreat",
                            "text": "改天再来",
                            "next_scene": "challenge_area",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "battle_ox_start",
                    "title": "战斗开始",
                    "text": "【战斗系统启动】\n\n人牛发出三道题目...\n\n(此处将调用RAG引擎生成题目)",
                    "auto_advance": True
                }
            ]
        },
        {
            "day": 3,
            "title": "裂痕",
            "default_scene": "day3_start",
            "scenes": [
                {
                    "scene_id": "day3_start",
                    "title": "觉醒的征兆",
                    "text": "第三天清晨，你醒来时感觉有些不同。\n\n脑海中似乎有什么东西在闪烁，像是沉睡已久的记忆正在苏醒。\n\n你的知识城池守护者——人级生肖——在身旁发出微光。\n\n「你正在接近觉醒的边缘。」它轻声说，「继续学习，唤醒你内在的力量。」",
                    "choices": [
                        {
                            "choice_id": "meditate",
                            "text": "静心感受变化",
                            "next_scene": "meditation_scene",
                            "effects": {"flags": {"attempted_meditation": True}}
                        },
                        {
                            "choice_id": "continue_training",
                            "text": "继续挑战",
                            "next_scene": "day3_training",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "meditation_scene",
                    "title": "冥想",
                    "text": "你闭上眼睛，感受体内的变化。\n\n渐渐地，周围的道开始向你汇聚——\n\n一道微弱的声音在脑海中响起：「生生不息……连续复习……三次……」\n\n这是某种能力的种子，正在你体内萌芽。",
                    "choices": [
                        {
                            "choice_id": "try_understand",
                            "text": "努力理解含义",
                            "next_scene": "reverberation_hint",
                            "effects": {"flags": {"heard_reverberation": True}}
                        },
                        {
                            "choice_id": "stop_meditation",
                            "text": "先专注挑战",
                            "next_scene": "day3_training",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "reverberation_hint",
                    "title": "回响的提示",
                    "text": "「回响」——这是你与生俱来的能力。\n\n当你满足特定条件时，这种能力会永久觉醒。\n\n「生生不息」回响：\n- 条件：连续复习同一知识点3次\n- 效果：复习效率提升50%\n\n守护者提醒你：「继续学习，解锁更多的回响。」",
                    "choices": [
                        {
                            "choice_id": "acknowledge",
                            "text": "我明白了",
                            "next_scene": "day3_training",
                            "effects": {"add_quest": "day3_discover_reverberation"}
                        }
                    ]
                },
                {
                    "scene_id": "day3_training",
                    "title": "第三日训练",
                    "text": "你来到挑战区，准备继续挑战人级生肖。\n\n昨天的战斗让你获得了宝贵的经验。\n\n今天，你可以挑战新的生肖，或者复习昨天的内容。",
                    "choices": [
                        {
                            "choice_id": "challenge_new",
                            "text": "挑战新生肖",
                            "next_scene": "challenge_area_day3",
                            "effects": {}
                        },
                        {
                            "choice_id": "review",
                            "text": "复习知识",
                            "next_scene": "review_session",
                            "effects": {"flags": {"doing_review": True}}
                        }
                    ]
                },
                {
                    "scene_id": "challenge_area_day3",
                    "title": "挑战区",
                    "text": "今天你可以挑战更多人级生肖：\n人鼠、人牛、人虎（昨天已解锁）",
                    "choices": [
                        {
                            "choice_id": "challenge_rat_2",
                            "text": "再次挑战人鼠",
                            "next_scene": "battle_rat",
                            "effects": {}
                        },
                        {
                            "choice_id": "skip_training",
                            "text": "跳过训练",
                            "next_scene": "day3_end",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "review_session",
                    "title": "复习环节",
                    "text": "你开始复习昨天学到的知识。\n\n守护者陪伴在侧，为你提供指导。\n\n【复习系统】\n- 选择要复习的知识模块\n- 答对3道题激活「生生不息」回响",
                    "choices": [
                        {
                            "choice_id": "review_python",
                            "text": "复习Python基础",
                            "next_scene": "day3_end",
                            "effects": {}
                        },
                        {
                            "choice_id": "skip_review",
                            "text": "跳过复习",
                            "next_scene": "day3_end",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "day3_end",
                    "title": "第三日结束",
                    "text": "【第3日结束】\n\n你已经感受到回响的存在……\n\n继续学习，解锁更多的力量。",
                    "auto_advance": False
                }
            ]
        },
        {
            "day": 4,
            "title": "分岔",
            "default_scene": "day4_start",
            "scenes": [
                {
                    "scene_id": "day4_start",
                    "title": "命运的岔路口",
                    "text": "第四天，你感觉自己已经不再是新手了。\n\n体内的道在流动，战绩逐渐累积。\n\n就在这时，几道身影出现在你面前——\n\n他们都带来了各自势力的邀请。",
                    "choices": [
                        {
                            "choice_id": "meet_chutianqiu",
                            "text": "与楚天秋交谈",
                            "next_scene": "chutianqiu_invite",
                            "effects": {"flags": {"met_chutianqiu": True}}
                        },
                        {
                            "choice_id": "meet_yanchunchun",
                            "text": "与燕知春交谈",
                            "next_scene": "yanchunchun_invite",
                            "effects": {"flags": {"met_yanchunchun": True}}
                        },
                        {
                            "choice_id": "meet_qianmeck",
                            "text": "与钱 Meck交谈",
                            "next_scene": "qianmeck_invite",
                            "effects": {"flags": {"met_qianmeck": True}}
                        },
                        {
                            "choice_id": "meet_chennan",
                            "text": "与陈俊南交谈",
                            "next_scene": "chennan_invite",
                            "effects": {"flags": {"met_chennan": True}}
                        }
                    ]
                },
                {
                    "scene_id": "chutianqiu_invite",
                    "title": "天堂口的邀请",
                    "text": "楚天秋站在你面前，气质沉稳，目光深邃。\n\n「我是楚天秋，天堂口的领袖。」\n\n「在这里独自行动很危险，但团结起来，我们就有机会打破轮回。」\n\n「天堂口不追求个人英雄主义，我们追求的是——一起离开。」",
                    "choices": [
                        {
                            "choice_id": "accept_heaven_gate",
                            "text": "加入天堂口",
                            "next_scene": "join_heaven_gate",
                            "effects": {
                                "faction": "heaven_gate",
                                "faction_reputation": {"heaven_gate": 30},
                                "add_quest": "heaven_gate_ch1",
                                "memory_fragment": {"type": "choice", "content": "加入了天堂口"}
                            }
                        },
                        {
                            "choice_id": "defer_decision",
                            "text": "需要再考虑一下",
                            "next_scene": "day4_choice_pending",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "yanchunchun_invite",
                    "title": "极道的邀请",
                    "text": "燕知春站在你面前，眼神如刀锋。\n\n「燕知春，极道。」\n\n「别相信什么团结合作，在这地方，拳头才是道理。」\n\n「想变强？想打破规则？那就跟我。极道会让你知道，什么叫真正的力量。」",
                    "choices": [
                        {
                            "choice_id": "accept_extremist",
                            "text": "加入极道",
                            "next_scene": "join_extremist",
                            "effects": {
                                "faction": "extremist",
                                "faction_reputation": {"extremist": 30},
                                "add_quest": "extremist_ch1",
                                "memory_fragment": {"type": "choice", "content": "加入了极道"}
                            }
                        },
                        {
                            "choice_id": "defer_decision",
                            "text": "需要再考虑一下",
                            "next_scene": "day4_choice_pending",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "qianmeck_invite",
                    "title": "貔貅的邀请",
                    "text": "钱 Meck笑眯眯地看着你，手里把玩着一枚金币。\n\n「钱 Meck，貔貅的当家的。」\n\n「这里最重要的是什么？道。」\n\n「貔貅可以帮你获取道——不管是情报、道具还是机会。只要你有足够的道，没有什么是买不到的。」",
                    "choices": [
                        {
                            "choice_id": "accept_fortune",
                            "text": "加入貔貅",
                            "next_scene": "join_fortune",
                            "effects": {
                                "faction": "fortune",
                                "faction_reputation": {"fortune": 30},
                                "add_quest": "fortune_ch1",
                                "memory_fragment": {"type": "choice", "content": "加入了貔貅"}
                            }
                        },
                        {
                            "choice_id": "defer_decision",
                            "text": "需要再考虑一下",
                            "next_scene": "day4_choice_pending",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "chennan_invite",
                    "title": "猫的邀请",
                    "text": "陈俊南悄然出现在你身后，声音低沉。\n\n「我是陈俊南。」\n\n「不要告诉任何人你的回响能力，也不要相信任何人。」\n\n「猫不追求力量或财富，我们追求的是——秘密。」",
                    "choices": [
                        {
                            "choice_id": "accept_shadow",
                            "text": "加入猫",
                            "next_scene": "join_shadow",
                            "effects": {
                                "faction": "shadow",
                                "faction_reputation": {"shadow": 30},
                                "add_quest": "shadow_ch1",
                                "memory_fragment": {"type": "choice", "content": "加入了猫"}
                            }
                        },
                        {
                            "choice_id": "defer_decision",
                            "text": "需要再考虑一下",
                            "next_scene": "day4_choice_pending",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "join_heaven_gate",
                    "title": "天堂口成员",
                    "text": "楚天秋微微一笑：「欢迎加入天堂口。」\n\n他递给你一枚刻有「天堂」二字的令牌。\n\n「从今天起，你就是我们的伙伴了。林檎会负责你的入门训练。」",
                    "choices": [
                        {
                            "choice_id": "continue",
                            "text": "继续",
                            "next_scene": "day4_after_faction",
                            "effects": {"inventory": ["天堂口令牌"]}
                        }
                    ]
                },
                {
                    "scene_id": "join_extremist",
                    "title": "极道成员",
                    "text": "燕知春满意地点头：「这才对。」\n\n她扔给你一枚刻有「极」字的徽章。\n\n「在极道，实力就是一切。证明你的价值，你会得到更多。」",
                    "choices": [
                        {
                            "choice_id": "continue",
                            "text": "继续",
                            "next_scene": "day4_after_faction",
                            "effects": {"inventory": ["极道徽章"]}
                        }
                    ]
                },
                {
                    "scene_id": "join_fortune",
                    "title": "貔貅成员",
                    "text": "钱 Meck笑着拍拍你的肩膀：「欢迎入伙。」\n\n他递给你一张黑卡：「这是你的貔貅股份证明。」\n\n「记住，在这里，道就是一切。」",
                    "choices": [
                        {
                            "choice_id": "continue",
                            "text": "继续",
                            "next_scene": "day4_after_faction",
                            "effects": {"inventory": ["貔貅黑卡"]}
                        }
                    ]
                },
                {
                    "scene_id": "join_shadow",
                    "title": "猫成员",
                    "text": "陈俊南递给你一枚漆黑的猫形徽章。\n\n「从现在起，你是猫的一员。」\n\n「记住我们的规矩——保密，不透露任何关于回响的事。违反者……不会有好下场。」",
                    "choices": [
                        {
                            "choice_id": "continue",
                            "text": "继续",
                            "next_scene": "day4_after_faction",
                            "effects": {"inventory": ["猫徽章"]}
                        }
                    ]
                },
                {
                    "scene_id": "day4_choice_pending",
                    "title": "暂不选择",
                    "text": "你告诉各势力代表，你需要更多时间考虑。\n\n他们表示理解，但警告你不要等太久——在这终焉之地，时间就是生命。\n\n【独立路线已解锁】",
                    "next_scene": "day4_after_faction",
                    "effects": {
                        "flags": {"independent_route": True}
                    }
                },
                {
                    "scene_id": "day4_after_faction",
                    "title": "第四日后续",
                    "text": "无论你做出了怎样的选择，第四日的挑战还在继续。\n\n是时候提升自己的实力，迎接接下来更艰难的考验了。\n\n地级生肖的挑战区域已经向你开放——如果你准备好了的话。",
                    "choices": [
                        {
                            "choice_id": "challenge_earth",
                            "text": "挑战地级生肖",
                            "next_scene": "day4_end",
                            "effects": {}
                        },
                        {
                            "choice_id": "train_human",
                            "text": "继续人级训练",
                            "next_scene": "day4_end",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "day4_end",
                    "title": "��四日结束",
                    "text": "【第4日结束】\n\n你的选择将影响接下来的剧情发展。\n\n每个势力都有自己的故事线……或者，你也可以走自己的路。",
                    "auto_advance": False
                }
            ]
        },
        {
            "day": 5,
            "title": "攻城",
            "default_scene": "day5_start",
            "scenes": [
                {
                    "scene_id": "day5_start",
                    "title": "攻城战",
                    "text": "第五天，你来到知识城池的核心区域。\n\n城中的道在召唤你，而地级生肖守护着通往深处的道路。\n\n每一个知识库都是一座城——而今天，你要攻下第一座。",
                    "choices": [
                        {
                            "choice_id": "begin_assault",
                            "text": "发起挑战",
                            "next_scene": "city_assault",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "city_assault",
                    "title": "攻城策略",
                    "text": "「选择你的攻城方式。」守护者声音响起。\n\n「正面突破需要绝对的实力……\n侧翼包抄需要掌握多个领域的知识……\n暗度陈仓需要灵活运用道具……」",
                    "choices": [
                        {
                            "choice_id": "head_on",
                            "text": "正面突破",
                            "next_scene": "battle_earth_direct",
                            "effects": {"flags": {"assault_type": "direct"}}
                        },
                        {
                            "choice_id": "flanking",
                            "text": "侧翼包抄",
                            "next_scene": "battle_earth_direct",
                            "effects": {"flags": {"assault_type": "flank"}}
                        },
                        {
                            "choice_id": "stealth",
                            "text": "暗度陈仓",
                            "next_scene": "battle_earth_direct",
                            "effects": {"flags": {"assault_type": "stealth"}}
                        }
                    ]
                },
                {
                    "scene_id": "battle_earth_direct",
                    "title": "地级挑战",
                    "text": "【地级生肖挑战】\n\n你选择正面迎敌——\n\n守护者发出5道题目，你需要答对至少4道。\n\n(战斗系统启动)",
                    "auto_advance": True
                }
            ]
        },
        {
            "day": 6,
            "title": "暗流",
            "default_scene": "day6_start",
            "scenes": [
                {
                    "scene_id": "day6_start",
                    "title": "势力冲突",
                    "text": "第六天，城中气氛变得微妙。\n\n你注意到各势力的成员之间有了更多的摩擦……\n\n似乎有什么正在酝酿之中。",
                    "choices": [
                        {
                            "choice_id": "investigate",
                            "text": "调查情况",
                            "next_scene": "investigate_conflict",
                            "effects": {"flags": {"investigating": True}}
                        },
                        {
                            "choice_id": "focus_self",
                            "text": "专注修炼",
                            "next_scene": "self_training_day6",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "investigate_conflict",
                    "title": "调查冲突",
                    "text": "你悄悄调查，发现了一些有趣的事情——\n\n天堂口和极道似乎在争夺某块区域的控制权……\n貔貅在暗中收集各方情报……\n而猫的活动比往常更加频繁……\n\n「势力战争即将开始。」有人在暗处低语。",
                    "choices": [
                        {
                            "choice_id": "support_faction",
                            "text": "支持势力",
                            "next_scene": "support_own_faction",
                            "effects": {"flags": {"taking_sides": True}}
                        },
                        {
                            "choice_id": "stay_neutral",
                            "text": "保持中立",
                            "next_scene": "remain_neutral",
                            "effects": {"flags": {"neutral": True}}
                        }
                    ]
                },
                {
                    "scene_id": "support_own_faction",
                    "title": "站队",
                    "text": "你决定支持自己的势力，参与即将到来的冲突。\n\n【势力战争系统已激活】\n完成势力任务可以获得额外奖励……\n但也可能招致敌对势力的敌视。",
                    "choices": [
                        {
                            "choice_id": "proceed",
                            "text": "继续",
                            "next_scene": "day6_end",
                            "effects": {"add_quest": "faction_war_participation"}
                        }
                    ]
                },
                {
                    "scene_id": "remain_neutral",
                    "title": "中立者",
                    "text": "你决定保持中立，不卷入势力纷争。\n\n【独立路线】\n中立可以让你获得各方势力的情报……\n但也可能让你成为各方的目标。",
                    "choices": [
                        {
                            "choice_id": "proceed",
                            "text": "继续",
                            "next_scene": "day6_end",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "self_training_day6",
                    "title": "自我修炼",
                    "text": "你选择不理会外界纷争，继续专注修炼。\n\n在终焉之地，实力才是最好的保障。",
                    "choices": [
                        {
                            "choice_id": "proceed",
                            "text": "继续",
                            "next_scene": "day6_end",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "day6_end",
                    "title": "第六日结束",
                    "text": "【第6日结束】\n\n暗流涌动，暴风雨即将来临……\n\n明天，你可能需要做出选择。",
                    "auto_advance": False
                }
            ]
        },
        {
            "day": 7,
            "title": "背叛",
            "default_scene": "day7_start",
            "scenes": [
                {
                    "scene_id": "day7_start",
                    "title": "抉择之日",
                    "text": "第七天，一切似乎都走到了十字路口。\n\n势力之间的矛盾已经无法调和……\n\n而你，必须做出最终的选择。",
                    "choices": [
                        {
                            "choice_id": "face_truth",
                            "text": "面对真相",
                            "next_scene": "reveal_truth",
                            "effects": {}
                        },
                        {
                            "choice_id": "continue_struggle",
                            "text": "继续抗争",
                            "next_scene": "day7_continue",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "reveal_truth",
                    "title": "真相揭示",
                    "text": "「你知道吗？」一个声音在耳边响起……\n\n「天龙，曾经也是觉醒者。」\n\n「第一个觉醒者。」\n\n这个真相改变了一切……但它也带来了新的问题：「你该如何面对这个真相？」",
                    "choices": [
                        {
                            "choice_id": "against_tianlong",
                            "text": "反抗天龙",
                            "next_scene": "rebel_path",
                            "effects": {"flags": {"against_tianlong": True}}
                        },
                        {
                            "choice_id": "understand_tianlong",
                            "text": "理解天龙",
                            "next_scene": "understand_path",
                            "effects": {"flags": {"understand_tianlong": True}}
                        }
                    ]
                },
                {
                    "scene_id": "rebel_path",
                    "title": "反抗之路",
                    "text": "「既然天龙也是觉醒者，那他可以被打败。」\n\n你决定反抗这不公的秩序。\n\n【反抗路线已开启】\n收集3位天级生肖的道，你就可以挑战天龙。",
                    "choices": [
                        {
                            "choice_id": "proceed",
                            "text": "继续",
                            "next_scene": "day7_end",
                            "effects": {"add_quest": "rebel_route"}
                        }
                    ]
                },
                {
                    "scene_id": "understand_path",
                    "title": "理解之路",
                    "text": "「也许……天龙有他的理由。」\n\n你决定先了解真相，再做决定。\n\n【理解路线已开启】\n找到天龙的过去，理解他创造终焉之地的原因。",
                    "choices": [
                        {
                            "choice_id": "proceed",
                            "text": "继续",
                            "next_scene": "day7_end",
                            "effects": {"add_quest": "understand_route"}
                        }
                    ]
                },
                {
                    "scene_id": "day7_continue",
                    "title": "继续抗争",
                    "text": "无论真相如何，你都要变得更强。\n\n天级的挑战在等待着真正的强者……",
                    "choices": [
                        {
                            "choice_id": "proceed",
                            "text": "继续",
                            "next_scene": "day7_end",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "day7_end",
                    "title": "第七日结束",
                    "text": "【第7日结束】\n\n路线已经确定，无法回头。\n\n第八日，天级挑战将开启……\n命运的齿轮正在转动。",
                    "auto_advance": False
                }
            ]
        },
        {
            "day": 8,
            "title": "天位",
            "default_scene": "day8_start",
            "scenes": [
                {
                    "scene_id": "day8_start",
                    "title": "天级挑战",
                    "text": "第八天，你站在了终焉之地的最高处。\n\n天级生肖的领域就在眼前——\n\n只有真正的强者才能在这里立足。\n\n而你的目标，是成为新的天龙……或者打败他。",
                    "choices": [
                        {
                            "choice_id": "begin_heaven_trial",
                            "text": "开始天级试炼",
                            "next_scene": "heaven_trial",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "heaven_trial",
                    "title": "天级试炼",
                    "text": "【天级生肖挑战】\n\n这是终焉之地最严苛的挑战——\n答对70%的题目只是最低要求……\n而且题目难度远超你的想象。\n\n(战斗系统启动)",
                    "auto_advance": True
                }
            ]
        },
        {
            "day": 9,
            "title": "抉择",
            "default_scene": "day9_start",
            "scenes": [
                {
                    "scene_id": "day9_start",
                    "title": "最终抉择",
                    "text": "第九天，明天就是最后一天。\n\n你已经走得很远……但终点就在眼前。\n\n「做出你的选择吧。」守护者说，「这将决定你的命运。」",
                    "choices": [
                        {
                            "choice_id": "final_prepare",
                            "text": "为最终决战做准备",
                            "next_scene": "final_preparation",
                            "effects": {}
                        },
                        {
                            "choice_id": "final_choice",
                            "text": "做出最终选择",
                            "next_scene": "make_final_choice",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "final_preparation",
                    "title": "准备阶段",
                    "text": "你利用最后的时间做最后的准备——\n\n整理道具\n复习知识\n确认状态\n\n一切就绪，明天就是终焉。",
                    "choices": [
                        {
                            "choice_id": "proceed",
                            "text": "进入最终日",
                            "next_scene": "day9_end",
                            "effects": {}
                        }
                    ]
                },
                {
                    "scene_id": "make_final_choice",
                    "title": "最终选择",
                    "text": "在这一刻，你必须明确自己的道路：\n\n反抗天龙？\n成为新的天龙？\n还是打破这一切？\n\n【选择不可逆转】",
                    "choices": [
                        {
                            "choice_id": "choose_rebel",
                            "text": "反抗天龙",
                            "next_scene": "day9_end",
                            "effects": {"flags": {"final_path": "rebel"}}
                        },
                        {
                            "choice_id": "choose_new_tianlong",
                            "text": "成为新天龙",
                            "next_scene": "day9_end",
                            "effects": {"flags": {"final_path": "new_tianlong"}}
                        },
                        {
                            "choice_id": "choose_break",
                            "text": "打破轮回",
                            "next_scene": "day9_end",
                            "effects": {"flags": {"final_path": "break_cycle"}}
                        }
                    ]
                },
                {
                    "scene_id": "day9_end",
                    "title": "第九日结束",
                    "text": "【第9日结束】\n\n一切准备就绪……\n\n明天，终焉之日，将决定一切。",
                    "auto_advance": False
                }
            ]
        },
        {
            "day": 10,
            "title": "终焉",
            "default_scene": "day10_start",
            "scenes": [
                {
                    "scene_id": "day10_start",
                    "title": "终焉之日",
                    "text": "第十天，最后一天。\n\n太阳升起，却带着不祥的光芒。\n\n所有的准备，所有的牺牲，所有的选择——\n都将在今天迎来终章。",
                    "choices": [
                        {
                            "choice_id": "confront_tianlong",
                            "text": "直面天龙",
                            "next_scene": "final_battle",
                            "effects": {"flags": {"final_battle": True}}
                        }
                    ]
                },
                {
                    "scene_id": "final_battle",
                    "title": "最终决战",
                    "text": "【天龙挑战】\n\n天龙站在你面前——\n他曾经也是觉醒者，就像你一样。\n\n「你来了。」他说，声音中带着一丝疲惫，\n「证明你有资格打破这一切。」\n\n(最终战斗系统启动)",
                    "auto_advance": True
                }
            ]
        }
    ],

    "branching_points": [
        {
            "day": 4,
            "condition": "faction_choice",
            "branches": {
                "heaven_gate": "heaven_gate_route",
                "extremist": "extremist_route",
                "fortune": "fortune_route",
                "shadow": "shadow_route",
                "independent": "independent_route"
            },
            "default_branch": "independent"
        },
        {
            "day": 7,
            "condition": "tianlong_knowledge",
            "branches": {
                "against": "rebel_route",
                "with": "understand_route"
            },
            "default_branch": "neutral_route"
        }
    ],

    "endings": [
        {
            "ending_id": "rebel",
            "title": "反抗者",
            "description": "你击败了天龙，打破了轮回，逃离了终焉之地",
            "conditions": {"zodiac_defeated": 3, "dao": 500},
            "final_battle": "tianlong"
        },
        {
            "ending_id": "new_tianlong",
            "title": "新天龙",
            "description": "你接受了天龙的传承，成为新的天龙",
            "conditions": {"dao": 500, "faction": "heaven_gate"},
            "final_battle": "tianlong"
        },
        {
            "ending_id": "wall_breaker",
            "title": "破壁者",
            "description": "你破解了终焉之地的规则，创造新的世界",
            "conditions": {"reverberations": ["time_rewind", "dream"]},
            "final_battle": None
        },
        {
            "ending_id": "accomplice",
            "title": "共犯",
            "description": "你与同伴一起打破规则，获得自由",
            "conditions": {"faction_count": 2},
            "final_battle": "tianlong"
        },
        {
            "ending_id": "cycle",
            "title": "轮回者",
            "description": "未能击败天龙，进入下一次轮回",
            "conditions": {},
            "final_battle": None
        },
        {
            "ending_id": "forgetter",
            "title": "遗忘者",
            "description": "你放弃一切，成为帮助后来者的存在",
            "conditions": {"dao": 0},
            "final_battle": None
        }
    ]
}