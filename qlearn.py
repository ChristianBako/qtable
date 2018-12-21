import random
import sys


DEFAULT_STATE = '       | ###  -| # #  +| # ####|       '


class Action:

    def __init__(self, name, dx, dy):
        self.name = name
        self.dx = dx
        self.dy = dy


ACTIONS = [
    Action('UP', 0, -1),
    Action('RIGHT', +1, 0),
    Action('DOWN', 0, +1),
    Action('LEFT', -1, 0)
]


class State:

    def __init__(self, env, x, y):
        self.env = env
        self.x = x
        self.y = y

    def clone(self):
        return State(self.env, self.x, self.y)

    def is_legal(self, action):
        cell = self.env.get(self.x + action.dx, self.y + action.dy)
        return cell is not None and cell in ' +-'

    def legal_actions(self, actions):
        legal = []
        for action in actions:
            if self.is_legal(action):
                legal.append(action)
        return legal

    def reward(self):
        cell = self.env.get(self.x, self.y)
        if cell is None:
            return None
        elif cell == '+':
            return +10
        elif cell == '-':
            return -10
        else:
            return 0

    def at_end(self):
        return self.reward() != 0

    def execute(self, action):
        self.x += action.dx
        self.y += action.dy
        return self

    def __str__(self):
        tmp = self.env.get(self.x, self.y)
        self.env.put(self.x, self.y, 'A')
        s = ' ' + ('-' * self.env.x_size) + '\n'
        for y in range(self.env.y_size):
            s += '|' + ''.join(self.env.row(y)) + '|\n'
        s += ' ' + ('-' * self.env.x_size)
        self.env.put(self.x, self.y, tmp)
        return s


class Env:

    def __init__(self, string):
        self.grid = [list(line) for line in string.split('|')]
        self.x_size = len(self.grid[0])
        self.y_size = len(self.grid)

    def get(self, x, y):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            return self.grid[y][x]
        else:
            return None

    def put(self, x, y, val):
        if x >= 0 and x < self.x_size and y >= 0 and y < self.y_size:
            self.grid[y][x] = val

    def row(self, y):
        return self.grid[y]

    def random_state(self):
        x = random.randrange(0, self.x_size)
        y = random.randrange(0, self.y_size)
        while self.get(x, y) != ' ':
            x = random.randrange(0, self.x_size)
            y = random.randrange(0, self.y_size)
        return State(self, x, y)


class QTable:

    def __init__(self, env, actions):
        self.env = env;
        self.actions = actions;
        self.qtable = [[[0 for z in xrange(len(ACTIONS))]  for x in xrange(env.x_size)] for y in xrange(env.y_size)]

    def get_q(self, state, action):
        return self.qtable[state.y][state.x][ACTIONS.index(action)]
    # return the value of the q table for the given state, action

    def get_q_row(self, state):
        return self.qtable[state.y][state.x]

    def set_q(self, state, action, val):
        self.qtable[state.y][state.x][ACTIONS.index(action)] = val


    def learn_episode(self, alpha=.10, gamma=.90):
        newState = self.env.random_state()

        ##Setup backpropagation
        newAction = random.choice(newState.legal_actions(self.actions))
        oldAction = newAction
        oldState = newState.clone()
        Oldq = self.get_q(oldState,oldAction)

        while not newState.at_end():
            newAction = random.choice(newState.legal_actions(self.actions))
            newState.execute(newAction)
            print newState

            newVal = (1-alpha) * Oldq + alpha*(newState.reward() + gamma*max(self.get_q_row(newState)))
            self.set_q(oldState,oldAction,newVal)
            oldAction = newAction
            oldState = newState.clone()
            Oldq = self.get_q(newState,newAction)




    # with the given alpha and gamma values,
    # from a random initial state,
    # consider a random legal action, execute that action,
    # compute the reward, and update the q table for (state, action).
    # repeat until an end state is reached (thus completing the episode)
    # also print the state at each state

    def learn(self, episodes, alpha=.10, gamma=.90):
        for episode in xrange(episodes):
            self.learn_episode(alpha,gamma)

    # run <episodes> number of episodes for learning with the given alpha and gamma

    def __str__(self):
        total = ""
        for action in ACTIONS:
            total = total + action.name + "\n"
            for x in self.qtable:
                empty = ""
                for y in x:
                    if y[ACTIONS.index(action)] == 0:
                        empty = empty + "----\t"
                    elif y[ACTIONS.index(action)]  < 0:
                            empty = empty + str(y[ACTIONS.index(action)])[0:5] + "\t"
                    else:
                        if str(y[ACTIONS.index(action)])[0:4] == "0.00":
                            empty = empty + "----\t"
                        else:
                            empty = empty + str(y[ACTIONS.index(action)])[0:4] + "\t"


                empty = empty + "\n"
                total = total + empty
        return total

# return a string for the q table as described in the assignment


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        env = Env(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STATE)
        if cmd == 'learn':
            qt = QTable(env, ACTIONS)
            qt.learn(100)
            print qt
