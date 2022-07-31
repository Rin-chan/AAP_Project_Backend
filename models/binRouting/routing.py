# Importing Deep Q-learning agent from Keras-RL
from cmath import inf
from rl.agents.dqn import Agent

# Using ORS service for distance
import openrouteservice
from openrouteservice.directions import directions

# Helper libraries
import numpy as np
import json
import os
import pickle
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"


with open('secrets.json', 'r') as f:
    apiKey = json.load(f)
  
client = openrouteservice.Client(key=apiKey["ORSKey"])

class DeliveryEnvironment(object):
    def __init__(self, coords, distances, n_stops):
        # Initialization
        self.coords = coords
        self.n_stops = n_stops
        self.action_space = self.n_stops
        self.observation_space = self.n_stops
        self.stops = []
        
        self._generate_stops(coords)
        self._generate_q_values(distances)

        # Initialize first point
        self.reset()


    def _generate_stops(self, coords):
        x = []
        y = []

        for coord in coords:
            x.append(coord[0])
            y.append(coord[1])

        self.x = x
        self.y = y


    def _generate_q_values(self, distances):
        self.q_stops = distances

        
    def pathDone(self):
        return self.stops


    def reset(self):
        self.stops = []

        first_stop = self.coords[0]
        self.stops.append(first_stop)

        return first_stop, 0


    def step(self,destination):
        # Get current state
        state = self._get_state()
        state_index = self.coords.index(state)
        new_state_index = destination
        new_state = self.coords[new_state_index]

        # Get reward for such a move
        reward = self._get_reward(state_index,new_state_index)

        # Append new_state to stops
        self.stops.append(new_state)
        done = len(self.stops) == self.n_stops

        return new_state,reward,done
    

    def _get_state(self):
        return self.stops[-1]
    

    def _get_reward(self,state,new_state):
        # Get distance
        allDist = self.q_stops[state]
        base_reward = allDist[new_state]
        return base_reward

class DeliveryQAgent(Agent):
    def __init__(self,states_size,actions_size,epsilon = 1.0,epsilon_min = 0.01,epsilon_decay = 0.999,gamma = 0.95,lr = 0.8):
        self.states_size = states_size
        self.actions_size = actions_size
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.gamma = gamma
        self.lr = lr
        self.Q = np.zeros([states_size,actions_size])

    def train(self,s,a,r,s_next):
        self.Q[s,a] = self.Q[s,a] + self.lr * (r + self.gamma*np.max(self.Q[s_next,a]) - self.Q[s,a])

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay


    def act(self,s):
        # Get Q Vector
        q = np.copy(self.Q[s,:])

        # Avoid already visited states
        q[self.states_memory] = -np.inf
        
        if np.random.rand() > self.epsilon:
            a = np.argmax(q)
        else:
            a = np.random.choice([x for x in range(self.actions_size) if x not in self.states_memory])
            
        return a
    
    def remember_state(self,s):
        self.states_memory.append(s)

    def reset_memory(self):
        self.states_memory = []
        
def run_episode(env,agent,coords):
    s,index = env.reset()
    agent.reset_memory()

    max_step = env.n_stops
    
    episode_reward = 0
    
    i = 0
    while i < max_step:
        agent.remember_state(index)

        a = agent.act(index)
        
        s_next,r,done = env.step(a)

        r = -1 * r
        
        qs = coords.index(s)
        qs_next = coords.index(s_next)
        
        agent.train(qs,a,r,qs_next)
        
        episode_reward += r
        s = s_next
        index = qs_next
        
        i += 1
        if done:
            break
            
    return env,agent,episode_reward

def run_n_episodes(env,agent,coords,n_episodes=500):
    global bestPath
    global bestScore

    for i in range(n_episodes):
        env,agent,episode_reward = run_episode(env,agent,coords)
        
        if bestScore < episode_reward:
            bestScore = episode_reward
            bestPath = env.pathDone()

    return env,agent

def getPath(binResult):
    global bestPath
    global bestScore
    bestPath = []
    bestScore = -inf
    
    coords = []
    
    for i in binResult:
        if i[3] == 1:
            coords.append((i[4], i[5]))
    
    routes = openrouteservice.distance_matrix.distance_matrix(client, coords, metrics=['distance']) # Get data of travel distance and time for a matrix of origins and destinations.

    routes_json = json.dumps(routes) # Convert to Json
    decoded_routes_json = json.loads(routes_json) # Read the Json

    env = DeliveryEnvironment(coords, decoded_routes_json["distances"], len(coords))
    agent = DeliveryQAgent(env.observation_space,env.action_space)
    
    env,agent = run_n_episodes(env,agent,coords)
    bestPath.append(coords[0])
    return bestPath