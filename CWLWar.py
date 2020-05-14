import requests
import json
import War
from War import clan_opp_status

"""
    CWLWar

        Instance Attributes

            tag: str
            state: str
            team_size: int
            preparation_start_time: str
            start_time: str
            end_time: str
            clan: CWLWarClan
            opponent: CWLWarClan

    CWLWarClan

        Instance Attributes

            status: str
            tag: str
            name: str
            lvl: int
            attack_count: int
            stars: int
            destruction_percentage: int
            members: list
                CWLWarMember

    CWLWarMember

        Instance Attributes

            tag: str
            name: str
            th_lvl: int
            map_position: int
            stars: int
            attacks: list
                CWLWarMemberAttack

    CWLWarMemberAttack

        Instance Attributes

            attacker_tag: str
            defender_tag: str
            stars: int
            destruction_percent: int
            order: int

"""


class CWLWar(War.War):
    def __init__(
        self,
        tag,
        state,
        team_size,
        preparation_start_time,
        start_time,
        end_time,
        clan,
        opponent
    ):
        super(CWLWar, self).__init__(
            state,
            team_size,
            preparation_start_time,
            start_time,
            end_time,
            clan,
            opponent
        )
        self.tag = tag


class CWLWarClan(War.WarClan):
    def __init__(
        self,
        status,
        tag,
        name,
        lvl,
        attack_count,
        stars,
        destruction_percentage,
        members
    ):
        War.WarClan.__init__(
            self,
            status,
            tag,
            name,
            lvl,
            attack_count,
            stars,
            destruction_percentage,
            members
        )


class CWLWarMember(War.WarMember):
    def __init__(
        self,
        tag,
        name,
        th_lvl,
        map_position,
        stars,
        attacks
    ):
        War.WarMember.__init__(
            self,
            tag,
            name,
            th_lvl,
            map_position,
            stars,
            attacks
        )


class CWLWarMemberAttack(War.WarMemberAttack):
    def __init__(
        self,
        attacker_tag,
        defender_tag,
        stars,
        destruction_percent,
        order
    ):
        War.WarMemberAttack.__init__(
            self,
            attacker_tag,
            defender_tag,
            stars,
            destruction_percent,
            order
        )


# getting the requested CWLWar data
def get(war_tag, clan_tag, header):
    war_json = json_response(war_tag, header)
    if war_json['state'] == 'notInWar':
        return CWLWar(
            war_tag,
            war_json['state'],
            0,
            0,
            0,
            0,
            0,
            0
        )
    else:
        # find whether the clan in clan_tag is clan
        # or opponent in the war_json
        clan_status, opp_status = clan_opp_status(war_json, clan_tag)

        # filling the clan members list (including the member attacks)
        clan_members = []
        for member in war_json[clan_status]['members']:
            member_attacks = []
            stars = 0

            if 'attacks' in member:
                for member_attack in member['attacks']:
                    stars += member_attack['stars']
                    member_attacks.append(CWLWarMemberAttack(
                        member_attack['attackerTag'],
                        member_attack['defenderTag'],
                        member_attack['stars'],
                        member_attack['destructionPercentage'],
                        member_attack['order'])
                    )
            # adding the current member to the list of clan members
            clan_members.append(CWLWarMember(
                member['tag'],
                member['name'],
                member['townhallLevel'],
                member['mapPosition'],
                stars,
                member_attacks)
            )
        # sorting clan members by map position
        clan_members = sorted(
            clan_members,
            key=lambda x: x.map_position,
            reverse=False
        )

        war_clan = CWLWarClan(
            clan_status,
            war_json[clan_status]['tag'],
            war_json[clan_status]['name'],
            war_json[clan_status]['clanLevel'],
            war_json[clan_status]['attacks'],
            war_json[clan_status]['stars'],
            war_json[clan_status]['destructionPercentage'],
            clan_members
        )

        # filling the opp members list (including the member attacks)
        opp_members = []
        for member in war_json[opp_status]['members']:
            member_attacks = []
            stars = 0

            if 'attacks' in member:
                for member_attack in member['attacks']:
                    stars += member_attack['stars']
                    member_attacks.append(CWLWarMemberAttack(
                        member_attack['attackerTag'],
                        member_attack['defenderTag'],
                        member_attack['stars'],
                        member_attack['destructionPercentage'],
                        member_attack['order'])
                    )
            # adding the current member to the list of opp members
            opp_members.append(CWLWarMember(
                member['tag'],
                member['name'],
                member['townhallLevel'],
                member['mapPosition'],
                stars,
                member_attacks)
            )
        # sorting opp members by map position
        opp_members = sorted(
            opp_members,
            key=lambda x: x.map_position,
            reverse=False
        )

        war_opp = CWLWarClan(
            opp_status,
            war_json[opp_status]['tag'],
            war_json[opp_status]['name'],
            war_json[opp_status]['clanLevel'],
            war_json[opp_status]['attacks'],
            war_json[opp_status]['stars'],
            war_json[opp_status]['destructionPercentage'],
            opp_members
        )

    return CWLWar(
        war_tag,
        war_json['state'],
        war_json['teamSize'],
        war_json['preparationStartTime'],
        war_json['startTime'],
        war_json['endTime'],
        war_clan,
        war_opp
    )


def json_response(tag, header):
    tag = tag[1:]
    url = f'https://api.clashofclans.com/v1/clanwarleagues/wars/%23{tag}'
    return requests.get(url, headers=header).json()
