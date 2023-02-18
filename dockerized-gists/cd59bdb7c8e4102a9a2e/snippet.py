# -*- coding: utf-8 -*-
import json
import operator
import re
import time
import threading
from datetime import datetime
from functools import partial
from getpass import getpass
from random import randint

import mechanize
import requests

def get_time():
    ''' 現在のunix timeをミリ秒単位13桁で返す '''
    return int(("%f" % time.time()).replace(".","")[:13])

def get_remain_time(t):
    ''' tまでの時間を秒単位で返す '''
    return (t - get_time()) / 1000

def sec_to_min(sec):
    return "%d分%d秒" % (sec/60, sec%60)

def printf(s):
    print s

prefix = "http://203.104.105.167"

class Communicator(object):
    ''' 通信手. APIを喋る. '''
    def __init__(self, mail, game_id):
        self.UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.75 Safari/535.7"
        self.headers = {'User-Agent':self.UA}

        print "please input DMM password"
        password = getpass()
        self.token = self._get_api_token(mail, password, game_id)
        self._start_api()

    def _list_to_str(self, list_):
        ''' [1,2,3]を'1,2,3'に変換する '''
        if len(list_) == 1:
            return str(list_[0])
        return ",".join(map(str, list_))

    def _parse_jsonp(self, jsonp):
        ''' jsonpパーサ '''
        index = jsonp.index("{")
        return json.loads(jsonp[index:])

    def _get_api_token(self, mail, password, game_id):
        br = mechanize.Browser()
        br.addheaders = [("User-agent",self.UA)]
        br.open("http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854/")
        br.select_form(nr=1)
        br["login_id"] = mail
        br["password"] = password
        response = br.submit()
        html = response.read()
        st =  re.search('[a-zA-Z0-9/+=]{220}', html).group()
        cookies_ = [cookie for cookie in br._ua_handlers['_cookies'].cookiejar]
        try:
            cookies = {
                "licenseUID":cookies_[6].value,
                "INT_SESID":cookies_[0].value,
                "check_done_login" : "1",
            }
        except IndexError:
            print "Error:ログインできません."
            exit()

        params = {
            "refresh":3600*24*31,
            "st":st,
            "authz":"signed",
            "url" : prefix + "/kcsapi/api_auth_member/dmmlogin/%s/1/%s" % (game_id, get_time()),
        }        

        res = requests.post("http://osapi.dmm.com/gadgets/makeRequest",
                params=params, cookies=cookies, headers=self.headers)
        try:
            return re.search('[a-z0-9]{40}?',res.text,re.U).group()
        except AttributeError:
            print res, res.text
            exit()

    def _start_api(self):
        url = prefix + "/kcs/mainD2.swf"
        params = {"api_token":self.token, "api_starttime":get_time()}
        requests.get(url, params=params, headers=self.headers)

    def _throw(self, url, extra_params={}):
        params = {"api_verno":"1", "api_token":self.token}
        params.update(extra_params)
        res = requests.post(url, params, headers=self.headers)
        if res.status_code == 200:
            return self._parse_jsonp(res.text)
        else:
            print "Error:Status Code, %d" % res.status_code, url
            return {}

    def basic(self):
        url = prefix + "/kcsapi/api_get_member/basic"
        return self._throw(url)

    def get_deck(self):
        url = prefix + "/kcsapi/api_get_member/deck"
        return self._throw(url)

    def start_mission(self, mission_id, deck_id):
        url = prefix + "/kcsapi/api_req_mission/start"
        params = {"api_deck_id":deck_id, "api_mission_id":mission_id}
        res = self._throw(url, params)
        print "遠征 艦隊:%d, No:%d" % (deck_id, mission_id), res.get("api_result_msg")
        return res

    def get_ships(self):
        url = prefix + "/kcsapi/api_get_member/ship2"
        params = {"api_sort_order":2, "api_sort_key":1}
        return self._throw(url, params)

    def get_all_ships(self):
        url = prefix + "/kcsapi/api_get_main/ship"
        return self._throw(url)

    def charge(self, ship_ids, kind):
        url = prefix + "/kcsapi/api_req_hokyu/charge"
        ship_ids = filter(lambda x:x!=-1, ship_ids)
        params = {
                "api_kind":kind, #燃料 1, #弾薬2, #全部3
                "api_id_items":self._list_to_str(ship_ids),
        }
        res = self._throw(url, params)
        print "補給 艦隊:%s, 種類:%d" % (self._list_to_str(ship_ids), kind), res.get("api_result_msg")
        return res

    def nyukyo(self, ship_id, ndock_id, highspeed=0):
        url = prefix + "/kcsapi/api_req_nyukyo/start"
        params = {
                "api_ship_id":ship_id,
                "api_ndock_id":ndock_id,
                "api_highspeed":highspeed,
        }
        res = self._throw(url, params)
        print "入渠 艦娘:%d, ドック:%d" % (ship_id, ndock_id), res.get("api_result_msg")
        return res

    def get_nyukyo_docks(self):
        url = prefix + "/kcsapi/api_get_member/ndock"
        res = self._throw(url)
        return res

    def get_mission_result(self, deck_id):

        url_result = prefix + "/kcsapi/api_req_mission/result"
        self._throw(prefix + "/kcsapi/api_get_member/actionlog")
        self._throw(prefix + "/kcsapi/api_auth_member/logincheck")
        self._throw(prefix + "/kcsapi/api_get_member/deck_port")
        self._throw(prefix + "/kcsapi/api_get_member/basic")

        res = self._throw(url_result, {"api_deck_id":deck_id})
        print "遠征結果取得 艦隊:%d" % deck_id, res.get("api_result_msg")
        print "資源:", res.get("api_data", {}).get("api_get_material", [])
        return res

    def start_battle(self, formation_id, deck_id, mapinfo_no, maparea_id):
        url_map = prefix + "/kcsapi/api_get_main/mapcell"
        url_start = prefix + "/kcsapi/api_req_map/start"

        start_params = {
                "api_formation_id":formation_id,
                "api_deck_id":deck_id,
                "api_mapinfo_no":mapinfo_no,
                "api_maparea_id":maparea_id,
        }

        res_map = self._throw(url_map, {"api_mapinfo_no":mapinfo_no, "api_maparea_id":maparea_id})
        res_start = self._throw(url_start, start_params)

        print "##################DEBUG### api_no:", res_start.get("api_data", {}).get("api_no", "") #debug

        enemy = res_start.get("api_data", {}).get("api_enemy", {})
        next = res_start.get("api_data", {}) .get("api_next", 0)
        no = res_start.get("api_data", {}).get("api_no", -1)
        return enemy, next, no

    def battle_result(self):
        url_result = prefix + "/kcsapi/api_req_sortie/battleresult"
        res_result = self._throw(url_result)
        result = res_result.get("api_data", {})
        print "戦闘結果:", result.get("api_quest_name"), ", ", result.get("api_win_rank")
        print "新しい仲間:", result.get("api_get_ship", {}).get("api_ship_name", u"無し")
        return result

    def battle(self, formation):
        url_battle = prefix + "/kcsapi/api_req_sortie/battle"
        res_battle = self._throw(url_battle, {"api_formation":formation})
        print "戦闘情報取得:",res_battle.get("api_result_msg")
        return res_battle

    def midnight_battle(self):
        url = prefix + "/kcsapi/api_req_battle_midnight/battle"
        res = self._throw(url)
        print "夜間戦闘情報取得", res.get("api_result_msg")
        return res

    def next(self):
        url_next = prefix + "/kcsapi/api_req_map/next"
        res_next = self._throw(url_next)
        print "次:", res_next.get("api_result_msg")
        print "##################DEBUG### api_no:", res_next.get("api_data", {}).get("api_no", "")
        enemy = res_next.get("api_data", {}).get("api_enemy", {})
        next = res_next.get("api_data", {}).get("api_next", 0)
        no = res_next.get("api_data", {}).get("api_no", -1)
        item = res_next.get("api_data", {}).get("api_itemget", {})
        print "アイテム取得:", item.get("api_id", "無し"), item.get("api_getcount", 0)
        return enemy, next, no

    def get_material(self):
        url = prefix + "/kcsapi/api_get_member/material"
        res = self._throw(url)
        materials = map(lambda d:d["api_value"], res.get("api_data", []))
        print "資源: " + " / ".join(map(str, materials))
        return materials

    def clear_quest(self, quest_id):
        url = prefix + "/kcsapi/api_req_quest/clearitemget"
        res = self._throw(url, {"api_quest_id":quest_id})
        print "任務完了 %d" % quest_id, res.get("api_result_msg")
        print "資源:", res.get("api_data", {}).get("api_material", "")
        return res

    def start_quest(self, quest_id):
        url = prefix + "/kcsapi/api_req_quest/start"
        res = self._throw(url, {"api_quest_id":quest_id})
        print "任務開始 %d" % quest_id, res.get("api_result_msg")
        return res

    def stop_quest(self, quest_id):
        url = prefix + "/kcsapi/api_req_quest/stop"
        res = self._throw(url, {"api_quest_id":quest_id})
        print "任務終了 %d" % quest_id, res.get("api_result_msg")
        return res

    def destroy_ship(self, ship_id):
        url = prefix + "/kcsapi/api_req_kousyou/destroyship"
        res = self._throw(url, {"api_ship_id":ship_id})
        return res

    def powerup(self, ship_id, items):
        url = prefix + "/kcsapi/api_req_kaisou/powerup"
        res = self._throw(url, {"api_id":ship_id, "api_id_items":self._list_to_str(items)})
        print "近代化改修", res.get("api_result_msg")
        return res

    def get_slotitems(self):
        url = prefix + "/kcsapi/api_get_member/slotitem"
        return self._throw(url)

    def get_all_slotitems(self):
        url = prefix + "/kcsapi/api_get_main/slotitem"
        return self._throw(url)

class BaseKankoreObject(object):
    def __init__(self, json):
        for key, value in json.items():
            setattr(self, key.replace("api_", ""), value)
    def __repr__(self):
        return self.name.encode("utf-8")

class MainSlotItem(BaseKankoreObject):
    @property
    def powerup_status(self):
        return [self.houg, self.raig, self.tyku, self.souk]

class SlotItem(MainSlotItem):
    pass

class Map(object):
    def __init__(self):
        pass

class Deck(object):
    def __init__(self, json):
        self.id = json["api_id"]
        self.name = json["api_name"]
        self.ships = json["api_ship"]
        mission = json["api_mission"]
        self.return_time = mission[2]
        self.mission_id = mission[1]
    def __repr__(self):
        return self.name.encode("utf-8")
    def in_mission(self):
        remain_time = get_remain_time(self.return_time)
        return remain_time > 0

class NDock(object):
    def __init__(self, json):
        self.id = json["api_id"]
        self.ship = json["api_ship_id"] # 0だと船無し
        self.complete_time = json["api_complete_time"]
        self.state = json["api_state"]
    def available(self):
        return self.state == 0
    def occupied(self):
        return self.state == 1
    def opened(self):
        return self.state != -1

class MainShip(BaseKankoreObject):
    pass

class Ship(object):
    def __init__(self, json):
        self.id = json["api_id"]
        self.bull = json["api_bull"]
        self.bull_max = ""
        self.fuel = json["api_fuel"]
        self.fuel_max = ""
        self.hp_ = json["api_nowhp"]
        self.hp_max = json["api_maxhp"]
        self.name = ""
        self.ndock_time = json["api_ndock_time"]
        self.cond = json["api_cond"]
        self.lv = json["api_lv"]
        self.powup = ""
        self.type = ""
        self.karyoku = json["api_karyoku"] #火力
        self.raisou = json["api_raisou"] #雷装
        self.taiku = json["api_taiku"] #対空
        self.soukou = json["api_soukou"] #装甲
        self.ship_id = json["api_ship_id"] #グローバルな艦娘id 
        self.exp = json["api_exp"]
        self.equips = filter(lambda x:x > 0, json["api_slot"])
    def __repr__(self):
        return self.name.encode("utf-8")
    def is_bull_max(self):
        return self.bull == self.bull_max
    def is_fuel_max(self):
        return self.fuel == self.fuel_max
    def is_both_max(self):
        return self.bull == self.bull_max and self.fuel == self.fuel_max
    def is_hp_max(self):
        return self.hp == 1
    def need_heal(self):
        return self.hp < 0.6
    def need_ndock(self):
        return self.hp != 1
    def need_fuel_charge(self):
        return (self.fuel / float(self.fuel_max)) < 0.5
    def need_bull_charge(self):
        return (self.bull / float(self.bull_max)) < 0.5
    def need_all_charge(self):
        return self.need_fuel_charge() or self.need_bull_charge()
    def is_tired(self):
        return self.cond <= 30
    def is_steel(self):
        return self.powup == [0,1,0,0] #火力, 雷装, 対空, 装甲
    def is_destroyer(self):
        return self.type == 2
    def is_newbie(self):
        return self.exp == 0
    @property
    def powerup_max(self):
        f = lambda list_:list_[1]
        return map(f, [self.karyoku, self.raisou, self.taiku, self.soukou])
    @property
    def powerup_now(self):
        f = lambda list_:list_[0]
        return map(f, [self.karyoku, self.raisou, self.taiku, self.soukou])
    @property
    def hp(self):
        return (self.hp_ / float(self.hp_max))
    @property
    def status(self):
        return  "%s: Lv %d, Cond %d HP %d/%d" % (self.name.encode("utf-8"),
                                    self.lv, self.cond, self.hp_, self.hp_max)

class GameController(object):
    def __init__(self, mail, game_id, threshold):
        self.comm = Communicator(mail, game_id)
        self.resource_threshold = threshold
        self.ships = []
        self.decks = []
        self.ndocks = []
        self.in_ndock_ships = []
        self.main_slot_items = map(MainSlotItem, self.comm.get_all_slotitems()["api_data"])
        self.main_ships = map(MainShip, self.comm.get_all_ships()["api_data"])
        self.update_slot_item()

    def set_ship_params(self, ship):
        main_ship = filter(lambda ms:ms.id == ship.ship_id, self.main_ships)[0]
        ship.name = main_ship.name
        ship.bull_max = main_ship.bull_max
        ship.fuel_max = main_ship.fuel_max
        ship.powup = main_ship.powup
        ship.type = main_ship.stype
        return ship

    def update_ships(self):
        ''' 船と艦隊のデータを更新 '''
        json = self.comm.get_ships()
        self.ships = map(self.set_ship_params, map(Ship, json["api_data"]))
        self.decks = map(Deck, json["api_data_deck"])

    def update_ndock(self):
        ''' 入渠データを更新 '''
        json = self.comm.get_nyukyo_docks()
        self.ndocks = map(NDock, json["api_data"])
        ship_ids = map(lambda d:d["api_ship_id"], json["api_data"])
        self.in_ndock_ships = filter(lambda s:s.id in ship_ids, self.ships)

    def update_slot_item(self):
        json = self.comm.get_slotitems()
        self.slot_items = map(SlotItem, json["api_data"])

    def get_ship_objects(self, ship_ids=[], deck_id=None):
        ''' 船のオブジェクトを返す '''
        deck_ship_ids = []
        if deck_id:
            deck_ship_ids = filter(lambda d:d.id == deck_id, self.decks)[0].ships
        ship_ids = ship_ids + deck_ship_ids
        return filter(lambda s:s.id in ship_ids, self.ships)

    def get_charge_ship_ids(self, deck_id, type="all"):
        ''' 補給すべき船のidを返す '''
        if type == "all":
            f = Ship.need_all_charge
        elif type == "fuel":
            f = Ship.need_fuel_charge
        elif type == "bull":
            f = Ship.need_bull_charge

        ship_objects = self.get_ship_objects(deck_id=deck_id)
        return map(lambda s:s.id, filter(f, ship_objects))

    def is_resource_too_low(self):
        ''' 資源が閾値以下ならTrueを返す '''
        materials = self.comm.get_material()
        if materials == []:
            return False
        oil, bullet = materials[0], materials[1]
        if oil < self.resource_threshold or bullet < self.resource_threshold:
            return True
        return False

    def nyukyo(self, ship_id):
        ''' 入渠する. 成功したらTrueを返す. '''
        self.update_ndock()
        self.update_ships()
        docks = filter(NDock.available, self.ndocks)
        if docks:
            self.comm.nyukyo(ship_id, docks[0].id)
            self.update_ndock()
            self.update_ships()
            return True

    def get_remain_dock_time(self, ship_id):
        ''' 船の入渠から返ってくる時間を返す '''
        occupied_docks = filter(NDock.occupied, self.ndocks)
        if ship_id in map(lambda s:s.id, self.in_ndock_ships):
            dock = filter(lambda d:d.ship == ship_id, occupied_docks)[0]
            return get_remain_time(dock.complete_time)
#        return 0

    def get_steel_ships(self):
#        steal_ships = filter(lambda s:s.is_steel() and s.is_destroyer() and s.is_newbie(), self.ships)
        steal_ships = filter(lambda s:s.is_destroyer() and s.is_newbie(), self.ships)
        return steal_ships

    def get_sozai_ships(self):
        light_cruiser_ids = [55, 56]
        destroyers = filter(lambda s:not s.is_steel() and s.is_destroyer() and s.is_newbie(), self.ships)
        light_cruisers = filter(lambda s:s.ship_id in light_cruiser_ids, self.ships)
        return light_cruisers + destroyers

    def get_ship_equips(self, ship):
        equips = filter(lambda i:i.id in ship.equips, self.slot_items)
        return equips

    def get_ship_powerup_margin(self, ship):
        powerup_max = ship.powerup_max
        powerup_now = ship.powerup_now
        equip_statuses = map(lambda e:e.powerup_status, self.get_ship_equips(ship))
        if equip_statuses != []:
            equip_powerup = reduce(lambda xs,ys:map(operator.add, xs,ys), equip_statuses)
        else:
            equip_powerup = [0,0,0,0]
        powerup_origin = map(operator.sub, powerup_now, equip_powerup)
        return map(operator.sub, powerup_max, powerup_origin)

    def can_powerup(self, ship, items):
        checkf = lambda xs,ys: map(operator.mul, xs,ys) == [0,0,0,0]
        powerup_statuses = reduce(lambda xs,ys:map(operator.add, xs,ys), map(lambda s:s.powup, items))
        if ship in self.in_ndock_ships:
            return False
        elif checkf(self.get_ship_powerup_margin(ship), powerup_statuses):
            return False
        else:
            return True

    def powerup(self, ship):
        print ship, self.get_ship_powerup_margin(ship), ship.id
        items = self.get_sozai_ships()
        if items == [] or len(items) <= 5:
            return ""
        elif not self.can_powerup(ship, items):
            return ""
        else:
            item_ids = map(lambda s:s.id, items)[:5]
            res = self.comm.powerup(ship.id, item_ids)
            self.update_ships()
            return res

class AI(GameController):
    def __init__(self, mail, game_id, threshold=2000):
        super(AI, self).__init__(mail, game_id, threshold)
        self.timers = []

    def kill_all_tasks(self):
        ''' 生きてるtimerオブジェクトをみんな殺す '''
        map(lambda t:t.cancel(), self.timers)

    def reserve_timer(self, name, time, function):
        ''' 次のお仕事を予約 '''
        self.timers = filter(lambda t:t.is_alive(), self.timers) #update timer
        timer = threading.Timer(time, function)
        now = datetime.now().strftime("%H:%M:%S")
        print "%s - %s : sleep %s" % (now, name, sec_to_min(time))
        self.timers.append(timer)
        timer.start()

    def auto_mission(self, deck_id, mission_id):
        ''' 自動で遠征するやつだよ '''
        self.update_ships()
        self.comm.get_material()
        deck = filter(lambda d: d.id == deck_id, self.decks)[0]

        if deck.in_mission():
            sleep_time = get_remain_time(deck.return_time)
        else:
            res = self.comm.get_mission_result(deck_id)
            #print "result:", res
            res = self.comm.charge(deck.ships, 3) #全部補充
            #print "charge:", res
            json = self.comm.start_mission(mission_id, deck_id)
            complete_time = json.get("api_data", {}).get("api_complatetime", 1800)
            sleep_time = get_remain_time(complete_time) - 40
        
        next_func = partial(self.auto_mission, deck_id, mission_id)
        self.reserve_timer("遠征", sleep_time, next_func)

    def auto_ndock(self, deck_id=1, exclude=False, all=False, reverse=False):
        ''' 自動で入渠するやつだよ '''
        self.update_ships()
        self.update_ndock()

        deck_ships = self.get_ship_objects(deck_id=deck_id)
        all_injured_ships = filter(lambda s:s.need_ndock(), self.ships)

        if all:
            nyukyo_ships = all_injured_ships
        elif exclude:
            nyukyo_ships = list(set(all_injured_ships) - set(deck_ships))

        nyukyo_ships = list(set(nyukyo_ships) - set(self.in_ndock_ships))
        nyukyo_ships = sorted(nyukyo_ships, key=lambda s:s.hp, reverse=reverse)

        for ship in nyukyo_ships:
            self.nyukyo(ship.id)

        if self.in_ndock_ships == []:
            return 
        in_ndock_ship_ids = map(lambda s:s.id, self.in_ndock_ships)
        sleep_time = min(map(self.get_remain_dock_time, in_ndock_ship_ids)) + 60
 
        next_func = partial(self.auto_ndock, deck_id, exclude, all)
        self.reserve_timer("入渠", sleep_time, next_func)

    def pre_battle_nyukyo_check(self, deck_id):
        ''' 戦闘前の入渠処理. sleepする秒数を返す.'''
        deck_ships = self.get_ship_objects(deck_id=deck_id)
        # 艦隊の誰かが入渠している場合
        in_ndock_deck_ships = list(set(deck_ships) & set(self.in_ndock_ships))
        if in_ndock_deck_ships:
            complete_time = 0
            for ship in in_ndock_deck_ships:
                complete_time = max(complete_time, self.get_remain_dock_time(ship.id))
            return complete_time

        injured_ships = filter(lambda s:s.need_heal(), deck_ships)
        if injured_ships == []:
            return 0
        need_nyukyo_ships = list(set(injured_ships) - set(self.in_ndock_ships))

        # 入渠すべき船がある場合
        complete_time = 0
        for ship in sorted(need_nyukyo_ships, key=lambda s:s.hp):
            if self.nyukyo(ship.id):
                complete_time = max(complete_time, self.get_remain_dock_time(ship.id))

        # 入渠できなかった場合
        if complete_time == 0:
            in_ndock_ship_ids = map(lambda s:s.id, self.in_ndock_ships)
            rdts = map(self.get_remain_dock_time, in_ndock_ship_ids)
            if rdts == []:
                return 0
            else:
                return min(map(self.get_remain_dock_time, in_ndock_ship_ids))
        else:
            return complete_time

    def auto_battle(self, deck_id, maparea_id, mapinfo_no, formation_id, formation, go_midnight=False, go_next=False):
        ''' 自動で戦闘するやつだよ '''
        self.update_ships()
        self.update_ndock()
        map(lambda s:printf(s.status), self.get_ship_objects(deck_id=deck_id))

        flag_can_battle = True
        sleep_time = self.pre_battle_nyukyo_check(deck_id)
        if sleep_time > 0:
            flag_can_battle = False
        charge_ship_ids = self.get_charge_ship_ids(deck_id)
        if charge_ship_ids:
            self.comm.charge(charge_ship_ids, 3)

        if self.is_resource_too_low():
            flag_can_battle = False
            decks = filter(lambda d: d.id != deck_id, self.decks)
            return_time = min(map(lambda d:d.return_time, decks))
            sleep_time = get_remain_time(return_time) + 60 #同時になるのを防ぐ
        
        if flag_can_battle:
            enemy, next, no = self.comm.start_battle(formation_id, deck_id, mapinfo_no, maparea_id)
            while True:
                if enemy:
                    battle_res = self.comm.battle(formation)
                    
                    sleep_time = self.pre_battle_nyukyo_check(deck_id)
                    if sleep_time > 0:
                        break

                    if go_midnight and battle_res["api_data"]["api_midnight_flag"] == 1:
                        self.comm.midnight_battle()
                    self.comm.battle_result()
                    
                    print "いらない子:", self.get_steel_ships()
                    map(lambda s:self.comm.destroy_ship(s.id), self.get_steel_ships())
                        
                    if go_next == False:
                        sleep_time = randint(20, 30)
                        break
                    
                    sleep_time = self.pre_battle_nyukyo_check(deck_id)
                    if sleep_time > 0:
                        break

                if next == 0:
                    sleep_time = randint(20, 30)
                    break
                enemy, next, no = self.comm.next()
                wait = randint(10, 20)
                print "待機 : %d sec" % wait
                time.sleep(wait)

        next_func = partial(self.auto_battle, deck_id, maparea_id, mapinfo_no, formation_id, formation, go_midnight, go_next)
        self.reserve_timer("戦闘", sleep_time, next_func)

    def auto_powerup(self, deck_id=1, kyouka_ship_ids=[]):
        self.update_ships()
        map(lambda s:printf(s.status), self.get_ship_objects(deck_id=deck_id))
        ships = self.get_ship_objects(deck_id=deck_id)
        if len(ships) > 1:
            print "Error: 艦娘を1人にしてください"
            return
        charge_ship_ids = self.get_charge_ship_ids(deck_id, type="bull")
        if charge_ship_ids:
            self.comm.charge(charge_ship_ids, 2)
        sleep_time = self.pre_battle_nyukyo_check(deck_id)
        if sleep_time == 0:
            self.comm.start_battle(1,1,1,1)
            self.comm.battle(1)
            self.comm.battle_result()

            self.update_ships()
            # いらない子を処分
            print "いらない子:", self.get_steel_ships()
            map(lambda s:self.comm.destroy_ship(s.id), self.get_steel_ships())
            print "素材:", self.get_sozai_ships()
            try:
                kyouka_ships = self.get_ship_objects(kyouka_ship_ids)
                res = map(self.powerup, kyouka_ships)
            except IndexError:
                pass

            sleep_time = randint(5,20)
        next_func = partial(self.auto_powerup, deck_id, kyouka_ship_ids)
        self.reserve_timer("自動強化", sleep_time, next_func)


    def collect_resouce(self, maps, deck_id=1, n=0):
        self.update_ships()
        self.comm.get_material()
        ships = self.get_ship_objects(deck_id=deck_id)
        if len(ships) > 1:
            print "Error: 艦娘を1人にしてください"
            return
        if n == len(maps):
            n = n - len(maps)

        break_condition = {
                           (2,1):(),
                           (3,4):(4,6,10,17),
                           (4,1):(2,3,9,11,12),
                           (4,2):(3,8,12,13),
                           (4,3):(5,8,16,19), 
                           }[maps[n]]
        maparea_id, mapinfo_no = maps[n]
        enemy, next, no = self.comm.start_battle(1, deck_id, mapinfo_no, maparea_id)

        while True:
            sleep_time = randint(20, 30)
            if next == 0:
                break

            if enemy:
                self.comm.battle(1)
                self.comm.battle_result()

            if no in break_condition:
                pass#break #なんか資源が増えないのでしばらくレベル上げ用に

            enemy, next, no = self.comm.next()

            wait = randint(5,10)
            print "待機 : %d秒" % wait
            time.sleep(wait)

        next_func = partial(self.collect_resouce, maps, deck_id, n+1)
        self.reserve_timer("資源回収", sleep_time, next_func)

if __name__ == "__main__":
    a = AI("", "", threshold=7000)
    a.auto_mission(2, 2)
    a.auto_mission(3, 3)
    a.auto_mission(4, 5)
    # 400/30/600/30, 100/250/250/250, 400/200/500/700
    # 4-2:鋼鉄, 3-4, 4-3:ボーキサイト, 4-1:燃料, - :弾薬                              
    #a.collect_resouce([(4,2)])
    #a.auto_battle(1, 22, 4, 0, 0, go_midnight=False, go_next=True)
    a.auto_powerup(kyouka_ship_ids=[656, 429, 644, 659, 3239, 4484, 3350, 13, 8701, 9949, 11445])
    a.auto_ndock(1, exclude=True) #入渠のバグがありそう
    #a.auto_ndock(all=True, reverse=True)
    while True:
        try:
            sleep_t = max(map(lambda t:t.interval, a.timers))
            time.sleep(sleep_t)
        except (KeyboardInterrupt, ValueError):
            a.kill_all_tasks()
            exit()
