"""
Chatbot intelligent pour League of Legends.
"""
from typing import Tuple, Optional, Dict, List, Any
from collections import deque
import json

from src.config.config import Config
from src.api.riot_api import RiotAPI
from src.api.huggingface_api import HuggingFaceAPI
from src.utils.text_processing import initialize_nltk, find_best_match

class LolChatbot:
    def __init__(self):
        """Initialisation du chatbot"""
        self.config = Config()
        self.riot_api = RiotAPI()
        self.huggingface_api = HuggingFaceAPI()
        initialize_nltk()
        
        # Historique des conversations avec contexte enrichi
        self.conversation_history = deque(maxlen=5)
        self.context = {
            "current_champion": None,
            "current_role": None,
            "skill_level": "beginner",  # beginner, intermediate, advanced, expert
            "last_topic": None
        }
        
        # Patterns d'intention enrichis
        self.intent_patterns = {
            "champion_info": ["qui est", "quel champion", "parle moi de", "raconte moi", "comment jouer", "explique"],
            "ability_info": ["capacité", "spell", "compétence", "q", "w", "e", "r", "passif", "sort", "ulti", "ultimate"],
            "role_info": ["role", "poste", "position", "lane", "jouer"],
            "item_info": ["objet", "item", "stuff", "build", "équipement", "acheter"],
            "gameplay_info": ["comment", "quand", "pourquoi", "stratégie", "technique"],
            "matchup_info": ["counter", "contre", "matchup", "synergie", "composition", "affinité"],
            "mechanics_info": ["mécanique", "combo", "technique", "astuce", "trick"],
            "tips_info": ["conseil", "astuce", "tip", "guide", "aide"],
            "stats_info": ["statistique", "stat", "dégât", "damage", "résistance", "armor", "mr"],
            "meta_info": ["meta", "tier", "fort", "faible", "populaire", "ban"]
        }
        
        # Patterns de salutations
        self.greetings = {
            "salut": "Salut invocateur ! Je suis votre assistant League of Legends. Je peux vous aider avec :\n- Des informations sur les champions\n- Des conseils de gameplay\n- Des stratégies de jeu\n- Des explications sur les rôles\n\nQue souhaitez-vous savoir ?",
            "bonjour": "Bonjour invocateur ! Je suis là pour vous aider à progresser dans League of Legends. Je peux vous conseiller sur :\n- Les champions et leurs capacités\n- Les builds et objets\n- Les stratégies de jeu\n- Les mécaniques de base\n\nQue voulez-vous apprendre ?",
            "hey": "Hey invocateur ! Prêt à devenir plus fort sur League of Legends ? Je peux vous aider avec :\n- L'analyse des champions\n- Les conseils de gameplay\n- Les builds optimaux\n- Les stratégies avancées\n\nSur quoi puis-je vous conseiller ?",
            "hello": "Bonjour invocateur ! En tant qu'assistant LoL, je peux vous aider à :\n- Maîtriser les champions\n- Comprendre les mécaniques\n- Optimiser vos builds\n- Améliorer votre gameplay\n\nQue souhaitez-vous explorer ?",
            "hi": "Salut invocateur ! Je suis votre coach LoL personnel. Je peux vous aider avec :\n- L'apprentissage des champions\n- Les stratégies de jeu\n- Les builds recommandés\n- Les conseils pro\n\nQue voulez-vous savoir ?"
        }

    def _enrich_champion_info(self, champion_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit les informations du champion avec des données supplémentaires"""
        if not champion_info:
            return None

        # Calculer les ratios et statistiques avancées
        stats = champion_info['stats']
        base_stats = {
            'hp': stats['hp'],
            'hp_per_level': stats['hpperlevel'],
            'mp': stats.get('mp', 0),
            'mp_per_level': stats.get('mpperlevel', 0),
            'armor': stats['armor'],
            'armor_per_level': stats['armorperlevel'],
            'mr': stats['spellblock'],
            'mr_per_level': stats['spellblockperlevel'],
            'attack_damage': stats['attackdamage'],
            'ad_per_level': stats['attackdamageperlevel'],
            'attack_speed': 0.625 / stats['attackspeed'],
            'as_per_level': stats['attackspeedperlevel']
        }

        # Calculer les statistiques pour différents niveaux
        levels_stats = {}
        for level in [1, 6, 11, 16, 18]:
            levels_stats[level] = {
                'hp': base_stats['hp'] + base_stats['hp_per_level'] * (level - 1),
                'mp': base_stats['mp'] + base_stats['mp_per_level'] * (level - 1),
                'armor': base_stats['armor'] + base_stats['armor_per_level'] * (level - 1),
                'mr': base_stats['mr'] + base_stats['mr_per_level'] * (level - 1),
                'ad': base_stats['attack_damage'] + base_stats['ad_per_level'] * (level - 1),
                'as': base_stats['attack_speed'] * (1 + (base_stats['as_per_level'] * (level - 1) / 100))
            }
            # Calculer le DPS théorique par niveau
            levels_stats[level]['dps'] = round(levels_stats[level]['ad'] * levels_stats[level]['as'], 2)

        # Enrichir avec les ratios des capacités
        ability_ratios = self._extract_ability_ratios(champion_info['abilities'])

        # Calculer les scores avancés
        enriched_stats = {
            'levels_stats': levels_stats,
            'ability_ratios': ability_ratios,
            'mobility': self._calculate_mobility_score(champion_info),
            'scaling': self._calculate_scaling_score(champion_info, ability_ratios),
            'damage_profile': self._calculate_damage_profile(champion_info, ability_ratios)
        }

        # Ajouter des conseils spécifiques basés sur les statistiques
        playstyle_tips = []
        if enriched_stats['damage_profile']['physical'] > 70:
            playstyle_tips.append("Fort potentiel de dégâts physiques")
        if enriched_stats['damage_profile']['magical'] > 70:
            playstyle_tips.append("Fort potentiel de dégâts magiques")
        if levels_stats[18]['hp'] > 2500:
            playstyle_tips.append("Très résistant en late game")
        if enriched_stats['mobility'] > 7:
            playstyle_tips.append("Grande mobilité")
        if enriched_stats['scaling'] > 7:
            playstyle_tips.append("Excellent scaling en late game")

        # Enrichir l'objet champion_info
        champion_info['enriched_stats'] = enriched_stats
        champion_info['playstyle_tips'] = playstyle_tips
        
        return champion_info

    def _extract_ability_ratios(self, abilities: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les ratios AP/AD des capacités"""
        ratios = {
            'passive': {'ap': 0, 'ad': 0, 'description': ''},
            'Q': {'ap': 0, 'ad': 0, 'description': ''},
            'W': {'ap': 0, 'ad': 0, 'description': ''},
            'E': {'ap': 0, 'ad': 0, 'description': ''},
            'R': {'ap': 0, 'ad': 0, 'description': ''}
        }

        # Analyser le passif
        passive_desc = abilities['passive']['description'].lower()
        ratios['passive']['ap'] = self._find_ratio(passive_desc, 'ap')
        ratios['passive']['ad'] = self._find_ratio(passive_desc, 'ad')
        ratios['passive']['description'] = passive_desc

        # Analyser les sorts
        for i, spell in enumerate(abilities['spells']):
            key = ['Q', 'W', 'E', 'R'][i]
            desc = spell['description'].lower()
            ratios[key]['ap'] = self._find_ratio(desc, 'ap')
            ratios[key]['ad'] = self._find_ratio(desc, 'ad')
            ratios[key]['description'] = desc

        return ratios

    def _find_ratio(self, text: str, ratio_type: str) -> float:
        """Trouve les ratios dans le texte"""
        import re
        ratio = 0
        pattern = r'(\d+(?:\.\d+)?)%\s*' + ('ap' if ratio_type == 'ap' else 'ad')
        matches = re.finditer(pattern, text)
        for match in matches:
            ratio += float(match.group(1)) / 100
        return ratio

    def _calculate_damage_profile(self, champion_info: Dict[str, Any], ability_ratios: Dict[str, Any]) -> Dict[str, float]:
        """Calcule le profil de dégâts du champion"""
        physical = 0
        magical = 0
        
        # Analyser les ratios des capacités
        for ability in ability_ratios.values():
            physical += ability['ad'] * 20  # Pondération arbitraire
            magical += ability['ap'] * 20   # Pondération arbitraire
            
        # Ajuster en fonction des tags et stats de base
        champion_tags = champion_info.get('tags', [])
        if isinstance(champion_tags, list):
            if "Mage" in champion_tags:
                magical += 30
            if "Marksman" in champion_tags:
                physical += 30
            if "Assassin" in champion_tags:
                if magical > physical:
                    magical += 20
                else:
                    physical += 20
                
        return {
            'physical': min(physical, 100),
            'magical': min(magical, 100)
        }

    def _calculate_mobility_score(self, champion_info: Dict[str, Any]) -> int:
        """Calcule un score de mobilité basé sur les capacités"""
        score = 5  # Score de base
        
        try:
            # Analyser les descriptions des sorts pour les mots-clés de mobilité
            mobility_keywords = ["dash", "saut", "bond", "téléportation", "vitesse", "speed"]
            abilities = champion_info.get('abilities', {})
            spells = abilities.get('spells', [])
            
            for spell in spells:
                description = spell.get('description', '').lower()
                if any(keyword in description for keyword in mobility_keywords):
                    score += 1
            
            # Ajuster en fonction des stats de base
            stats = champion_info.get('stats', {})
            if stats.get('movespeed', 0) > 340:
                score += 1
                
        except Exception as e:
            print(f"Erreur lors du calcul du score de mobilité: {str(e)}")
            return 5  # Score par défaut en cas d'erreur
            
        return min(score, 10)  # Plafonner à 10

    def _calculate_scaling_score(self, champion_info: Dict[str, Any], ability_ratios: Dict[str, Any]) -> int:
        """Calcule un score de scaling basé sur les ratios et stats"""
        score = 5  # Score de base
        
        # Analyser les ratios AP/AD dans les descriptions des sorts
        for spell in champion_info['abilities']['spells']:
            if "% AD" in spell['description']:
                score += 0.5
            if "% AP" in spell['description']:
                score += 0.5
                
        # Ajuster en fonction des stats par niveau
        if ability_ratios['Q']['ad'] > 0 or ability_ratios['W']['ad'] > 0 or ability_ratios['E']['ad'] > 0 or ability_ratios['R']['ad'] > 0:
            score += 1
        if ability_ratios['Q']['ap'] > 0 or ability_ratios['W']['ap'] > 0 or ability_ratios['E']['ap'] > 0 or ability_ratios['R']['ap'] > 0:
            score += 1
            
        return min(score, 10)  # Plafonner à 10

    def _format_conversation_history(self) -> str:
        """Formate l'historique de conversation pour le contexte"""
        if not self.conversation_history:
            return ""
        
        history = "\nHistorique de la conversation:\n"
        for q, r in self.conversation_history:
            history += f"Q: {q}\nR: {r}\n"
        return history
    
    def _get_champion_response(self, query: str) -> Optional[str]:
        """Génère une réponse enrichie pour une question sur un champion"""
        try:
            for pattern in self.intent_patterns["champion_info"]:
                if pattern in query:
                    champion_name = query.replace(pattern, "").strip("? ").lower()
                    champion_info = self.riot_api.get_champion_info(champion_name)
                    
                    if champion_info:
                        # Enrichir les informations
                        champion_info = self._enrich_champion_info(champion_info)
                        if not champion_info:
                            return "Désolé, je n'ai pas pu récupérer les informations enrichies pour ce champion."
                        
                        # Construire une réponse détaillée
                        response = f"{champion_info['name']} est {champion_info.get('title', '')}.\n\n"
                        
                        if 'lore' in champion_info:
                            response += f"Histoire : {champion_info['lore'][:200]}...\n\n"
                        
                        # Stats enrichies
                        if 'enriched_stats' in champion_info:
                            response += "Statistiques avancées :\n"
                            if 'levels_stats' in champion_info['enriched_stats'] and 18 in champion_info['enriched_stats']['levels_stats']:
                                level_18_stats = champion_info['enriched_stats']['levels_stats'][18]
                                response += f"- DPS théorique : {level_18_stats.get('dps', 'N/A')}\n"
                                response += f"- Survie : {level_18_stats.get('hp', 'N/A')}\n"
                            
                            response += f"- Mobilité : {champion_info['enriched_stats'].get('mobility', 5)}/10\n"
                            response += f"- Scaling : {champion_info['enriched_stats'].get('scaling', 5)}/10\n\n"
                        
                        # Style de jeu
                        if 'playstyle_tips' in champion_info and champion_info['playstyle_tips']:
                            response += "Points forts :\n"
                            for tip in champion_info['playstyle_tips']:
                                response += f"- {tip}\n"
                            response += "\n"
                        
                        # Conseils de jeu
                        if 'tips' in champion_info and 'ally' in champion_info['tips'] and champion_info['tips']['ally']:
                            response += "Conseils pour jouer ce champion :\n"
                            for tip in champion_info['tips']['ally'][:2]:
                                response += f"- {tip}\n"
                        
                        # Mettre à jour le contexte
                        self.context["current_champion"] = champion_name
                        self.context["last_topic"] = "champion_info"
                        
                        return response
                    
            return None
        except Exception as e:
            print(f"Erreur lors de la génération de la réponse: {str(e)}")
            return "Désolé, une erreur s'est produite lors de la récupération des informations du champion."
    
    def _get_ability_response(self, query: str) -> Optional[str]:
        """Génère une réponse enrichie pour une question sur une capacité"""
        words = query.split()
        champion_name = self.context.get("current_champion")
        ability_key = None
        
        # Détecter le champion et la capacité
        for word in words:
            if "d'" in word:
                champion_name = word.split("d'")[1]
            for key in ["q", "w", "e", "r", "passif", "ulti", "ultimate"]:
                if key in word.lower():
                    ability_key = key if key != "ulti" and key != "ultimate" else "r"
        
        if champion_name and ability_key:
            champion_info = self.riot_api.get_champion_info(champion_name)
            if champion_info:
                champion_info = self._enrich_champion_info(champion_info)  # Enrichir les informations
                
                if ability_key == 'passif':
                    ability = champion_info['abilities']['passive']
                    ratios = champion_info['enriched_stats']['ability_ratios']['passive']
                    
                    response = f"Passif de {champion_info['name']} - {ability['name']}:\n"
                    response += f"{ability['description']}\n\n"
                    
                    # Ajouter les ratios s'ils existent
                    if ratios['ap'] > 0 or ratios['ad'] > 0:
                        response += "Ratios :\n"
                        if ratios['ap'] > 0:
                            response += f"- {ratios['ap'] * 100}% AP\n"
                        if ratios['ad'] > 0:
                            response += f"- {ratios['ad'] * 100}% AD\n"
                    
                    return response
                else:
                    spell_index = {'q': 0, 'w': 1, 'e': 2, 'r': 3}[ability_key]
                    spell = champion_info['abilities']['spells'][spell_index]
                    ratios = champion_info['enriched_stats']['ability_ratios'][ability_key.upper()]
                    
                    response = f"Capacité {ability_key.upper()} de {champion_info['name']} - {spell['name']}:\n"
                    response += f"{spell['description']}\n\n"
                    
                    # Informations techniques détaillées
                    response += "Informations techniques :\n"
                    response += f"- Cooldown par niveau : {', '.join(map(str, spell['cooldown']))} secondes\n"
                    
                    if spell['cost'][0] > 0:
                        costs = spell['cost']
                        cost_type = spell.get('costType', 'mana')
                        response += f"- Coût par niveau : {', '.join(map(str, costs))} {cost_type}\n"
                    
                    if spell['range'][0] > 0:
                        ranges = spell['range']
                        response += f"- Portée par niveau : {', '.join(map(str, ranges))} unités\n"
                    
                    # Ajouter les ratios s'ils existent
                    if ratios['ap'] > 0 or ratios['ad'] > 0:
                        response += "\nRatios :\n"
                        if ratios['ap'] > 0:
                            response += f"- {ratios['ap'] * 100}% AP\n"
                        if ratios['ad'] > 0:
                            response += f"- {ratios['ad'] * 100}% AD\n"
                    
                    return response
        
        return None
    
    def _get_matchup_response(self, query: str, champion_name: str) -> Optional[str]:
        """Génère une réponse enrichie pour une question sur les matchups"""
        try:
            # Détecter le rôle
            role = self.context.get("current_role")
            for word in query.split():
                if word in ["top", "jungle", "mid", "bot", "support"]:
                    role = word
                    self.context["current_role"] = role
                    break
            
            # Si pas de rôle spécifié, utiliser le rôle principal du champion
            if not role:
                champion_info = self.riot_api.get_champion_info(champion_name)
                if champion_info and 'recommended_roles' in champion_info:
                    role = champion_info['recommended_roles'][0]
                    self.context["current_role"] = role
            
            if role:
                matchups = self.riot_api.get_champion_matchups(champion_name, role)
                if matchups:
                    response = f"Analyse des matchups pour {champion_name.capitalize()} en {role} :\n\n"
                    
                    # Contre-picks avec explications
                    response += "Contre-picks difficiles :\n"
                    for counter in matchups["counter_picks"][:3]:
                        response += f"- {counter}\n"
                    
                    # Matchups favorables
                    response += "\nMatchups favorables :\n"
                    for good_against in matchups["good_against"][:3]:
                        response += f"- {good_against}\n"
                    
                    # Synergies
                    response += "\nMeilleures synergies :\n"
                    for synergy in matchups["synergies"][:3]:
                        response += f"- {synergy}\n"
                    
                    return response
            
            return f"Je n'ai pas trouvé d'informations sur les matchups de {champion_name}. Essayez de préciser un rôle (top, jungle, mid, bot, support)."
            
        except Exception as e:
            print(f"Erreur lors de la génération des matchups: {str(e)}")
            return None
    
    def _is_greeting(self, query: str) -> bool:
        """Vérifie si la requête est une salutation"""
        query = query.lower().strip()
        return query in self.greetings or any(greeting in query for greeting in self.greetings.keys())
    
    def _get_greeting_response(self, query: str) -> str:
        """Retourne une réponse appropriée à une salutation"""
        query = query.lower().strip()
        for greeting in self.greetings.keys():
            if greeting in query:
                return self.greetings[greeting]
        return self.greetings["salut"]  # Réponse par défaut
    
    def _get_champion_specific_response(self, champion_name: str, topic: str) -> Optional[str]:
        """Génère une réponse spécifique pour un champion et un sujet"""
        champion_info = self.riot_api.get_champion_info(champion_name)
        if not champion_info:
            return None
            
        # Réponses pour les sujets de base
        if topic in ["mana", "mana management", "gestion mana"]:
            response = f"Conseils de gestion de mana pour {champion_info['name']} :\n"
            if champion_info['stats'].get('mp', 0) > 0:
                response += "1. Gérez votre mana en early game\n"
                response += f"2. Mana de base : {champion_info['stats']['mp']}\n"
                response += f"3. Régénération de mana : {champion_info['stats']['mpregen']}\n"
                response += "4. Privilégiez les objets avec mana et régénération"
            else:
                response += "Ce champion n'utilise pas de mana comme ressource."
            return response
            
        elif topic in ["trade", "trades", "trading"]:
            response = f"Conseils de trade pour {champion_info['name']} :\n"
            response += "1. Utilisez vos points forts :\n"
            if champion_info['info']['attack'] > 7:
                response += "- Fort en auto-attaques\n"
            if champion_info['info']['magic'] > 7:
                response += "- Fort en dégâts magiques\n"
            if champion_info['info']['defense'] > 7:
                response += "- Bonne survie en trade\n"
            response += f"\n2. Distance d'attaque : {champion_info['stats']['attackrange']}\n"
            return response
            
        elif topic in ["position", "positionnement"]:
            response = f"Conseils de positionnement pour {champion_info['name']} :\n"
            if "Marksman" in champion_info['tags']:
                response += "1. Restez derrière votre équipe\n"
                response += "2. Maintenez votre distance de sécurité\n"
            elif "Tank" in champion_info['tags']:
                response += "1. Positionnez-vous devant votre équipe\n"
                response += "2. Protégez vos carries\n"
            elif "Assassin" in champion_info['tags']:
                response += "1. Cherchez des angles de flank\n"
                response += "2. Attendez les moments clés\n"
            else:
                response += "1. Adaptez votre position selon la situation\n"
                response += "2. Restez à portée de vos alliés\n"
            return response
            
        # Description générale si aucun sujet spécifique
        return champion_info['description']

    def _get_stats_response(self, champion_name: str) -> Optional[str]:
        """Génère une réponse détaillée pour les statistiques d'un champion"""
        try:
            champion_info = self.riot_api.get_champion_info(champion_name)
            if not champion_info:
                return None

            # Enrichir les informations
            champion_info = self._enrich_champion_info(champion_info)
            if not champion_info:
                return None

            response = f"Statistiques complètes de {champion_info['name']} :\n\n"

            # Statistiques de base
            stats = champion_info['stats']
            response += "Statistiques de base (niveau 1) :\n"
            response += f"- PV : {stats['hp']} (+{stats['hpperlevel']} par niveau)\n"
            if stats.get('mp', 0) > 0:
                response += f"- Mana : {stats['mp']} (+{stats['mpperlevel']} par niveau)\n"
            response += f"- Armure : {stats['armor']} (+{stats['armorperlevel']} par niveau)\n"
            response += f"- Résistance magique : {stats['spellblock']} (+{stats['spellblockperlevel']} par niveau)\n"
            response += f"- Dégâts d'attaque : {stats['attackdamage']} (+{stats['attackdamageperlevel']} par niveau)\n"
            response += f"- Vitesse d'attaque : {round(0.625 / stats['attackspeed'], 2)} (+{stats['attackspeedperlevel']}% par niveau)\n"
            response += f"- Vitesse de déplacement : {stats['movespeed']}\n\n"

            # Statistiques aux niveaux clés
            response += "Statistiques aux niveaux clés :\n"
            for level in [6, 11, 16, 18]:
                level_stats = champion_info['enriched_stats']['levels_stats'][level]
                response += f"\nNiveau {level} :\n"
                response += f"- PV : {round(level_stats['hp'])}\n"
                if level_stats['mp'] > 0:
                    response += f"- Mana : {round(level_stats['mp'])}\n"
                response += f"- Armure : {round(level_stats['armor'])}\n"
                response += f"- Résistance magique : {round(level_stats['mr'])}\n"
                response += f"- Dégâts d'attaque : {round(level_stats['ad'])}\n"
                response += f"- DPS théorique : {level_stats['dps']}\n"

            # Profil de dégâts
            damage_profile = champion_info['enriched_stats']['damage_profile']
            response += "\nProfil de dégâts :\n"
            response += f"- Dégâts physiques : {damage_profile['physical']}/100\n"
            response += f"- Dégâts magiques : {damage_profile['magical']}/100\n"

            # Scores calculés
            response += "\nScores d'évaluation :\n"
            response += f"- Mobilité : {champion_info['enriched_stats']['mobility']}/10\n"
            response += f"- Scaling : {champion_info['enriched_stats']['scaling']}/10\n"

            return response

        except Exception as e:
            print(f"Erreur lors de la génération des statistiques: {str(e)}")
            return None

    def get_response(self, query: str) -> str:
        """Génère une réponse à la question de l'utilisateur en utilisant le contexte"""
        if not query or len(query.strip()) < 2:
            return "Je suis désolé, votre question est trop courte. Pourriez-vous la reformuler ?"
        
        query = query.lower().strip()
        
        # Détecter le niveau de compétence dans la question
        if any(word in query for word in ["débutant", "commencer", "débuter"]):
            self.context["skill_level"] = "beginner"
        elif any(word in query for word in ["intermédiaire", "moyen"]):
            self.context["skill_level"] = "intermediate"
        elif any(word in query for word in ["avancé", "expert", "pro"]):
            self.context["skill_level"] = "expert"
        
        # Vérifier si c'est une salutation
        if self._is_greeting(query):
            response = self._get_greeting_response(query)
            self.conversation_history.append((query, response))
            return response
        
        # Extraire le nom du champion et le rôle de la question
        champion_name = None
        role = None
        
        # Chercher d'abord dans le contexte
        champion_name = self.context.get("current_champion")
        role = self.context.get("current_role")
        
        # Puis dans la question
        words = query.split()
        for word in words:
            # Vérifier si le mot est un champion
            if self.riot_api.get_champion_info(word):
                champion_name = word
                self.context["current_champion"] = word
            # Vérifier si le mot est un rôle
            elif word in ["top", "jungle", "mid", "bot", "support"]:
                role = word
                self.context["current_role"] = word
        
        if champion_name:
            # Détecter le type de question en priorité
            is_stats_question = any(word in query for word in ["stat", "statistique", "dégât", "damage", "résistance"])
            is_counter_question = any(word in query for word in ["counter", "contre", "matchup", "versus", "vs", "affinité"])
            is_ability_question = any(word in query for word in ["capacité", "spell", "sort", "q", "w", "e", "r", "ulti", "passive", "passif"])
            
            # Traiter la question selon son type
            if is_stats_question:
                stats_response = self._get_stats_response(champion_name)
                if stats_response:
                    self.conversation_history.append((query, stats_response))
                    return stats_response
            
            elif is_counter_question:
                matchup_response = self._get_matchup_response(query, champion_name)
                if matchup_response:
                    self.conversation_history.append((query, matchup_response))
                    return matchup_response
            
            elif is_ability_question:
                ability_response = self._get_ability_response(query)
                if ability_response:
                    self.conversation_history.append((query, ability_response))
                    return ability_response
            
            # Questions générales sur le champion
            champion_response = self._get_champion_response(query)
            if champion_response:
                self.conversation_history.append((query, champion_response))
                return champion_response
            
            # Questions spécifiques sur un aspect du champion
            for topic in ["mana", "trade", "position", "combo", "objectif"]:
                if topic in query:
                    specific_response = self._get_champion_specific_response(champion_name, topic)
                    if specific_response:
                        self.conversation_history.append((query, specific_response))
                        self.context["last_topic"] = topic
                        return specific_response
        
        # En dernier recours, utiliser l'API HuggingFace avec le contexte enrichi
        try:
            context_prompt = self._build_context_prompt()
            conversation_history = self._format_conversation_history()
            response = self.huggingface_api.get_response(query + context_prompt + conversation_history)
            if response:
                self.conversation_history.append((query, response))
                return response
        except Exception as e:
            print(f"Erreur HuggingFace: {str(e)}")
        
        return "Je ne suis pas sûr de comprendre votre question. Essayez de la reformuler en précisant le champion et le type d'information que vous recherchez (statistiques, capacités, counters, etc.)."

    def _build_context_prompt(self) -> str:
        """Construit un prompt enrichi avec le contexte actuel"""
        context_prompt = "\nContexte actuel :\n"
        
        if self.context["current_champion"]:
            champion_info = self.riot_api.get_champion_info(self.context["current_champion"])
            if champion_info:
                context_prompt += f"- Champion : {champion_info['name']}\n"
                if 'tags' in champion_info:
                    context_prompt += f"- Type : {', '.join(champion_info['tags'])}\n"
        
        if self.context["current_role"]:
            context_prompt += f"- Rôle : {self.context['current_role']}\n"
        
        if self.context["skill_level"]:
            context_prompt += f"- Niveau de jeu : {self.context['skill_level']}\n"
        
        if self.context["last_topic"]:
            context_prompt += f"- Dernier sujet abordé : {self.context['last_topic']}\n"
        
        return context_prompt 