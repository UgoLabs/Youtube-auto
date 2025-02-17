import math
import random

class MCTSTreeNode:
    def __init__(self, state, parent=None):
        """
        state: typically an index (of a subtopic) from a cluster.
        parent: the parent node in the MCTS tree.
        """
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.unexplored_actions = None

def simulate_topic_outcome(topic_text: str) -> float:
    """
    Simulates an outcome for a topic (could be replaced by a predictive model).
    """
    base_score = random.random() + (0.01 * len(topic_text))
    return base_score

def expand_node(node: MCTSTreeNode, cluster):
    """
    Expands the node by adding a child for one unexplored subtopic index.
    """
    if node.unexplored_actions is None:
        node.unexplored_actions = list(range(len(cluster)))
    if not node.unexplored_actions:
        return None
    next_action = node.unexplored_actions.pop()
    child_node = MCTSTreeNode(state=next_action, parent=node)
    node.children.append(child_node)
    return child_node

def rollout(cluster, child_state: int) -> float:
    """
    Performs a rollout simulation for the chosen subtopic.
    """
    topic_text = cluster[child_state]
    return simulate_topic_outcome(topic_text)

def backpropagate(node: MCTSTreeNode, reward: float):
    """
    Propagates the reward back up the tree.
    """
    current = node
    while current is not None:
        current.visits += 1
        current.value += reward
        current = current.parent

def select_child(node: MCTSTreeNode, c=1.41):
    """
    Selects a child node using the UCB1 algorithm.
    """
    best_child = None
    best_score = -float('inf')
    for child in node.children:
        if child.visits == 0:
            return child
        exploitation = child.value / child.visits
        exploration = c * math.sqrt(2 * math.log(node.visits) / child.visits)
        score = exploitation + exploration
        if score > best_score:
            best_score = score
            best_child = child
    return best_child

def mcts_best_topic(cluster, simulations=50) -> str:
    """
    Uses MCTS to select the best topic from a cluster.
    """
    root = MCTSTreeNode(state=None)
    root.unexplored_actions = list(range(len(cluster)))
    
    for _ in range(simulations):
        node = root
        while node.children and node.unexplored_actions == []:
            node = select_child(node)
        if node.unexplored_actions:
            child = expand_node(node, cluster)
        else:
            child = node
        reward = rollout(cluster, child.state)
        backpropagate(child, reward)
    
    best_node = max(root.children, key=lambda n: (n.value / n.visits) if n.visits else -999)
    return cluster[best_node.state]
