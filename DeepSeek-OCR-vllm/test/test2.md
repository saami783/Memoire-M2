# Approximation Ratios of Graph Neural Networks for Combinatorial Problems  


Ryoma Sato \(^{1,2}\) Makoto Yamada \(^{1,2,3}\) Hisashi Kashima \(^{1,2}\) \(^{1}\) Kyoto University \(^{2}\) RIKEN AIP \(^{3}\) JST PRESTO \(\{r.\mathrm{sato}@\mathrm{ml}.\mathrm{ist}.\mathrm{i},\mathrm{myamada}@\mathrm{i},\mathrm{kashima}@\mathrm{i}\}\) . kyoto- u.ac.jp  


## Abstract  


In this paper, from a theoretical perspective, we study how powerful graph neural networks (GNNs) can be for learning approximation algorithms for combinatorial problems. To this end, we first establish a new class of GNNs that can solve a strictly wider variety of problems than existing GNNs. Then, we bridge the gap between GNN theory and the theory of distributed local algorithms. We theoretically demonstrate that the most powerful GNN can learn approximation algorithms for the minimum dominating set problem and the minimum vertex cover problem with some approximation ratios with the aid of the theory of distributed local algorithms. We also show that most of the existing GNNs such as GIN, GAT, GCN, and GraphSAGE cannot perform better than with these ratios. This paper is the first to elucidate approximation ratios of GNNs for combinatorial problems. Furthermore, we prove that adding coloring or weak- coloring to each node feature improves these approximation ratios. This indicates that preprocessing and feature engineering theoretically strengthen model capabilities.  


## 1 Introduction  


Graph neural networks (GNNs) [8, 9, 12, 22] is a novel machine learning method for graph structures. GNNs have achieved state- of- the- art performance in various tasks, including chemoinformatics [7], question answering systems [23], and recommendation systems [31], to name a few.  


Recently, machine learning methods have been applied to combinatorial problems [4, 11, 16, 27] to automatically obtain novel and efficient algorithms. Xu et al. [30] analyzed the capability of GNNs for solving the graph isomorphism problem, and they found that GNNs cannot solve it but they are as powerful as the Weisfeiler- Lehman graph isomorphism test.  


The minimum dominating set problem, minimum vertex cover problem, and maximum matching problem are examples of important combinatorial problems other than the graph isomorphism problem. These problems are all NP- hard. Therefore, under the assumption that \(\mathrm{P} \neq \mathrm{NP}\) , GNNs cannot exactly solve these problems because they run in polynomial time with respect to input size. For NP- hard problems, many approximation algorithms have been proposed to obtain sub- optimal solutions in polynomial time [25], and approximation ratios of these algorithms have been studied to guarantee the performance of these algorithms.  


In this paper, we study the approximation ratios of algorithms that GNNs can learn for combinatorial problems. To analyze the approximation ratios of GNNs, we bridge the gap between GNN theory and the theory of distributed local algorithms. Here, distributed local algorithms are distributed algorithms that use only a constant number of synchronous communication rounds [1, 10, 24]. Thanks to their relationship with distributed local algorithms, we can elucidate the lower bound of the approximation ratios of algorithms that GNNs can learn for combinatorial problems. As an example of our

<--- Page Split --->
results, if the input feature of each node is the node degree alone, no GNN can solve \((\Delta +1 - \epsilon)\) - approximation for the minimum dominating set problem or \((2 - \epsilon)\) - approximation for the minimum vertex cover problem, where \(\epsilon >0\) is any real number and \(\Delta\) is the maximum node degree.  


In addition, thanks to this relationship, we find vector- vector consistent GNNs ( \(\mathrm{VV}_{\mathrm{C}}\) - GNNs), which are a novel class of GNNs. \(\mathrm{VV}_{\mathrm{C}}\) - GNNs have strictly stronger capability than existing GNNs and have the same capability as a computational model of distributed local algorithms. Based on our key finding, we propose the consistent port numbering GNNs (CPNGNNs), which is the most powerful GNN model among \(\mathrm{VV}_{\mathrm{C}}\) - GNNs. That is, for any graph problem that a \(\mathrm{VV}_{\mathrm{C}}\) - GNN can solve, there exists a parameter of CPNGNNs that can also solve it. Interestingly, CPNGNNs are strictly more powerful than graph isomorphism networks (GIN), which were considered to be the most powerful GNNs [30]. Furthermore, CPNGNNs achieve optimal approximation ratios among GNNs: CPNGNNs can solve \((\Delta +1)\) - approximation for the minimum dominating set problem and 2- approximation for the minimum vertex cover problem.  


However, these approximation ratios are unsatisfactory because they are as high as those of simple greedy algorithms. One of the reasons for these high approximation ratios is that we only use node degrees as node features. We show that adding coloring or weak coloring to each node feature strengthens the capability of GNNs. For example, if we use weak 2- coloring as a node feature in addition to node degree, CPNGNNs can solve \((\frac{\Delta + 1}{2})\) - approximation for the minimum dominating set problem. Considering that any graph has weak 2- coloring and that we can easily calculate weak 2- coloring in linear time, it is interesting that such preprocessing and feature engineering can theoretically strengthen the model capability.  


The contributions of this paper are summarized as follows:  


- We reveal the relationships between the theory of GNNs and distributed local algorithms. Namely, we show that the set of graph problems that GNN classes can solve is the same as the set of graph problems that distributed local algorithm classes can solve.- We propose CPNGNNs, which is the most powerful GNN among the proposed GNN class.- We elucidate the approximation ratios of GNNs for combinatorial problems including the minimum dominating set problem and the minimum vertex cover problem. This is the first paper to elucidate the approximation ratios of GNNs for combinatorial problems.  


## 2 Related Work  


### 2.1 Graph Neural Networks  


GNNs were first introduced by Gori et al. [8] and Scarselli et al. [22]. They obtained the node embedding by recursively applying the propagation function until convergence. Recently, Kipf and Welling [12] proposed graph convolutional networks (GCN), which significantly outperformed existing methods, including non- neural network- based approaches. Since then, many graph neural networks have been proposed, such as GraphSAGE [9] and the graph attention networks (GATs) [26].  


Vinyals et al. [27] proposed pointer networks, which can solve combinatorial problems on a plane, such as the convex hull problem and the traveling salesman problem. Bello et al. [4] trained pointer networks using reinforcement learning to automatically obtain novel algorithms for these problems. Note that pointer networks are not GNNs. However, we introduce them here because they were the first to solve combinatorial problems using deep learning. Khalil et al. [11] and Li et al. [16] used GNNs to solve combinatorial problems. They utilized search methods with GNNs, whereas we use only GNNs to focus on the capability of GNNs.  


Xu et al. [30] analyzed the capability of GNNs. They showed that GNNs cannot solve the graph isomorphism problem and that the capability of GNNs is at most the same as that of the Weisfeiler- Lehman graph isomorphism test. They also proposed the graph isomorphism networks (GIN), which are as powerful as the Weisfeiler- Lehman graph isomorphism test. Therefore, the GIN is the most powerful GNNs. The motivation of this paper is the same as that of Xu et al.'s work [30] but we consider not only the graph isomorphism problem but also the minimum dominating set problem, minimum vertex cover problem, and maximum matching problem. Furthermore, we find the approximation ratios of these problems for the first time and propose GNNs more powerful than GIN.

<--- Page Split --->
Require: Graph \(G = (V,E,X)\) ; Parameters \(\theta\) ; Aggregation function \(f_{\theta}^{(l)}(l = 1,\ldots ,L)\) .  


Ensure: Embedding of nodes \(z\in \mathbb{R}^{n\times d_{L + 1}}\)  


1: \(z_{v}^{(1)}\gets x_{v}\) \(\forall v\in V)\)  


2: for \(l = 1,\ldots ,L\) do  


3: for \(v_{l}\in V\) do  


4: \(z_{v}^{(l + 1)}\gets f_{\theta}^{(l)}\) (aggregated information from neighbor nodes of \(v\) )  


5: end for  


6: end for  


7: return \(z^{(L + 1)}\)  


### 2.2 Distributed Local Algorithms  


A distributed local algorithm is a distributed algorithm that runs in constant time. More specifically, in a distributed local algorithm, we assume each node has infinite computational resources and decides the output within a constant number of communication rounds with neighboring nodes. For example, distributed local algorithms are used for controlling wireless sensor networks [13], constructing self- stabilization algorithms [14, 18], and building sublinear- time algorithms [20].  


Distributed local algorithms were first studied by Angluin [1], Linial [17], and Naor and Stockmeyer [18]. Angluin [1] showed that deterministic distributed algorithms cannot find a center of a graph without any unique node identifiers. Linial [17] showed that no distributed local algorithms can solve 3- coloring of cycles, and they require \(\Omega (\log^{*}n)\) communication rounds for distributed algorithms to solve the problem. Naor and Stockmeyer [18] showed positive results for distributed local algorithms for the first time. For example, distributed local algorithms can find weak 2- coloring and solve a variant of the dining philosophers problem. Later, several non- trivial distributed local algorithms were found, including 2- approximation for the minimum vertex cover problem [2].  


There are many computational models of distributed local algorithms. Some computational models use unique identifiers of nodes [18], port numbering [1], and randomness [19, 28], and other models do not [10]. Furthermore, some results use the following assumptions about the input: degrees are bounded [2], degrees are odd [18], graphs are planar [6], and graphs are bipartite [3]. In this paper, we do not use any unique identifiers nor randomness, but we do use port numbering, and we assume the degrees are bounded. We describe our assumptions in detail in Section 3.1.  


## 3 Preliminaries  


### 3.1 Problem Setting  


Here, we first describe the notation used in this paper and then we formulate the graph problem.  


Notation. For a positive integer \(k\in \mathbb{Z}^{+}\) , let \([k]\) be the set \(\{1,2,\ldots ,k\}\) . Let \(G = (V,E,X)\) be a input graph, where \(V\) is a set of nodes, \(E\) is a set of edges, and \(X\in \mathbb{R}^{|V|\times d_{0}}\) is a feature matrix. We represent an edge of a graph \(G = (V,E,X)\) as an unordered pair \(\{u,v\}\) with \(u,v\in V\) . We write \(n = |V|\) for the number of nodes and \(m = |E|\) for the number of edges. The nodes \(V\) are considered to be numbered with \([n]\) . (i.e., we assume \(V = [n]\) .) For a node \(v\in V\) , \(\deg (u)\) denotes the degree of node \(v\) and \(\mathcal{N}(v)\) denotes the set of neighbors of node \(v\) .  


A GNN model \(N_{\theta}(G,v)\) is a function parameterized by \(\theta\) that takes a graph \(G\) and a node \(v\in V\) as input and output the label \(y_{v}\in Y\) of node \(v\) , where \(Y\) is a set of labels. We study the expression capability of the function family \(N_{\theta}\) for combinatorial graph problems with the following assumptions.  


Assumption 1 (Bounded- Degree Graphs). In this paper, we consider only bounded- degree graphs. In other words, for a fixed (but arbitrary) constant \(\Delta\) , we assume that the degree of each node of the input graphs is at most \(\Delta\) . This assumption is natural because there are many bounded- degree graphs in the real world. For example, degrees in molecular graphs are bounded by four, and the degrees in computer networks are bounded by the number of LAN ports of routers. Moreover, the bounded

<--- Page Split --->
degree assumption is often used in distributed local algorithms [17, 18, 24]. For each positive integer \(\Delta \in \mathbb{Z}^{+}\) , let \(\mathcal{F}(\Delta)\) be the set of all graphs with maximum degrees of \(\Delta\) at most.  


Assumption 2 (Node Features). We do not consider node features other than those that can be derived from the input graph itself for focusing on graph theoretic properties. When there are no node features available, the degrees of nodes are sometimes used [9, 21, 30]. Therefore, we use only the degree of a node as the node feature (i.e., \(\boldsymbol{z}_{v}^{(1)} = \mathrm{ONEHOT}(\deg (v))\) unless specified. Later, we show that using coloring or weak coloring of the input graph in addition to degrees of nodes as node features makes models theoretically more powerful.  


Graph Problems. A graph problem is a function \(\Pi\) that associates a set \(\Pi (G)\) of solutions with each graph \(G = (V,E)\) . Each solution \(S\in \Pi (G)\) is a function \(S\colon V\to Y\) \(Y\) is a finite set that is independent of \(G\) . We say a GNN model \(N_{\theta}\) solves a graph problem \(\Pi\) if for any \(\Delta \in \mathbb{Z}^{+}\) , there exists a parameter \(\theta\) such that for any graph \(G\in \mathcal{F}(\Delta)\) \(N_{\theta}(G,\cdot)\) is in \(\Pi (G)\) . For example, let \(Y\) be a set of labels of nodes, let \(L(G)\colon V\to Y\) be the ground truth of a multi- label classification problem for a graph \(G\) (i.e., \(L(G)(v)\) denotes the ground truth label of node \(v\in V\) ), and let \(\Pi (G) =\) \(\{f\colon V\to \{0,1\} \mid |\{v\in V\mid f(v) = L(G)(v)\} |\geq 0.9\cdot |V|\}\) . This graph problem \(\Pi\) corresponds to a multi- label classification problem. A GNN model \(N_{\theta}\) solves \(\Pi\) means there exists a parameter \(\theta\) of the model such that achieves an accuracy 0.9 for this problem. Other examples of graph problems are combinatorial problems. Let \(C(G)\subset V\) be the minimum vertex cover of a graph \(G\) , let \(Y = \{0,1\}\) and let \(\Pi (G) = \{f\colon V\to \{0,1\} \mid D = \{v\mid f(v) = 1\}\) is a vertex cover and \(|D|\leq 2\cdot |C(G)|\}\) . This graph problem \(\Pi\) corresponds to 2- approximation for the minimum vertex cover problem.  


### 3.2 Known Model Classes  


We introduce two known classes of GNNs, which include GraphSAGE [9], GCN [12], GAT [26], and GIN [30].  


MB- GNNs. A layer of an existing GNN can be written as  


\[\boldsymbol{z}_{v}^{(l + 1)} = f_{\theta}^{(l)}(\boldsymbol{z}_{v}^{(l)},\mathrm{MULTISET}(\boldsymbol{z}_{u}^{(l)}\mid u\in \mathcal{N}(v))),\]  


where \(f_{\theta}^{(l)}\) is a learnable aggregation function. We call GNNs that can be written in this form multiset- broadcasting GNNs (MB- GNNs) — multiset because they aggregate features from neighbors as a multiset and broadcasting because for any \(v\in \mathcal{N}(u)\) , the "message" [7] from \(u\) to \(v\) is the same (i.e., \(\boldsymbol{z}_{u}\) ). GraphSAGE- mean [9] is an example of MB- GNNs because a layer of GraphSAGE- mean is represented by the following equation:  


\[\boldsymbol{z}_{v}^{(l + 1)} = \mathrm{CONCAT}(\boldsymbol{z}_{v}^{(l)},\frac{1}{|\mathcal{N}(v)|}\sum_{u\in \mathcal{N}(v)}\boldsymbol{W}^{(l)}\boldsymbol{z}_{u}^{(l)}),\]  


where CONCAT concatenates vectors into one vector. Other examples of MB- GNNs are GCN [12], GAT [26], and GIN [30].  


\[\boldsymbol{z}_{v}^{(l + 1)} = f_{\theta}^{(1)}(\boldsymbol{z}_{v}^{(l)},\mathrm{SET}(\boldsymbol{z}_{u}^{(l)}\mid u\in \mathcal{N}(v))).\]  


GraphSAGE- pool [9] is an example of SB- GNNs because a layer of GraphSAGE- mean is represented by the following equation:.  


\[\boldsymbol{z}_{v}^{(l + 1)} = \max \{\{\sigma (\boldsymbol{W}^{(l)}\boldsymbol{z}_{u}^{(l)} + \boldsymbol{b}^{(l)})\mid u\in \mathcal{N}(v)\} \} .\]  


Clearly, SB- GNNs are a subclass of MB- GNNs. Xu et al. [30] discussed the differences in capability of SB- GNNs and MB- GNNs. We show that MB- GNNs are strictly stronger than SB- GNNs in another way in this paper.  


## 4 Novel Class of GNNs  


In this section, we first introduce a GNN class that is more powerful than MB- GNNs and SB- GNNs. To make GNN models more powerful than MB- GNNs, we introduce the concept of port numbering [1, 10] to GNNs.

<--- Page Split --->
Port Numbering. A port of a graph \(G\) is a pair \((v,i)\) , where \(v\in V\) and \(i\in [\deg (v)]\) . Let \(P(G) = \{(v,i)\mid v\in V,i\in [\deg (v)]\}\) be the set of all ports of a graph \(G\) . A port numbering of a graph \(G\) is the function \(p\colon P(G)\to P(G)\) such that for any edge \(\{u,v\}\) , there exist \(i\in [\deg (u)]\) and \(j\in [\deg (v)]\) such that \(p(u,i) = (v,j)\) . We say that a port numbering is consistent if \(p\) is an involution (i.e., \(\forall (v,i)\in P(G)\) \(p(p(v,i)) = (v,i)\) ). We define the functions \(p_{\mathrm{tail}}\colon V\times \Delta \to V\cup \{- \}\) and \(p_{\mathrm{n}}\colon V\times \Delta \to \Delta \cup \{- \}\) as follows:  


\[p_{\mathrm{tail}}(v,i) = \left\{ \begin{array}{ll}u\in V(\exists j\in [\deg (u)]s.t.p(u,j) = (v,i)) & (i\leq \deg (v))\\ - & (\mathrm{otherwise}), \end{array} \right.\]  


\[p_{\mathrm{n}}(v,i) = \left\{ \begin{array}{ll}j\in [\deg (p_{\mathrm{tail}}(v,i))] (p(p_{\mathrm{tail}}(v,i),j) = (v,i)) & (i\leq \deg (v))\\ - & (\text{otherwise}), \end{array} \right.\]  


where - is a special symbol that denotes the index being out of range. Note that these functions are well- defined because there always exists only one \(u\in V\) for \(p_{\mathrm{tail}}\) and \(j\in [\deg (p_{\mathrm{tail}}(v,i))]\) for \(p_{\mathrm{n}}\) if \(i\leq \deg (v)\) . Intuitively, \(p_{\mathrm{tail}}(v,i)\) represents the node that sends messages to the port \(i\) of node \(v\) and \(p_{\mathrm{n}}(v,i)\) represents the port number of the node \(p_{\mathrm{tail}}(v,i)\) that sends messages to the port \(i\) of node \(v\) .  


The GNN class we introduce in the following uses a consistent port numbering to calculate embeddings. Intuitively, SB- GNNs and MB- GNNs send the same message to all neighboring nodes. GNNs can send different messages to neighboring nodes by using port numbering, and this strengthens model capability.  


\(\mathbf{V}\mathbf{V}_{\mathbf{C}}\) - GNNs. Vector- vector consistent GNNs (VVc- GNNs) are a novel class of GNNs that we introduce in this paper. They calculate an embedding with the following formula:  


\[z_{v}^{(l + 1)} = f_{\theta}^{(l)}(z_{v}^{(l)},z_{p_{\mathrm{tail}}^{(l)}(v,1)}^{(l)},p_{\mathrm{n}}(v,1),z_{p_{\mathrm{tail}}(v,2)}^{(l)},p_{\mathrm{n}}(v,2),\ldots ,z_{p_{\mathrm{tail}}(v,\Delta)}^{(l)},p_{\mathrm{n}}(v,\Delta)).\]  


If the index of \(z\) is the special symbol -, we also define the embedding as the special symbol - (i.e., \(z_{- } = - )\) . To calculate embeddings of nodes of a graph \(G\) using a GNN with port numbering, we first calculate one consistent port numbering \(p\) of \(G\) , and then we input \(G\) and \(p\) to the GNN. Note that we can calculate a consistent port numbering of a graph in linear time by numbering edges one by one. We say a GNN class \(\mathcal{N}\) with port numbering solves a graph problem \(\Pi\) if for any \(\Delta \in \mathbb{Z}^{+}\) , there exists a GNN \(N_{\theta}\in \mathcal{N}\) and its parameter \(\theta\) such that for any graph \(G\in \mathcal{F}(\Delta)\) , for any consistent port numbering \(p\) of \(G\) , the output \(N_{\theta}(G,p,\cdot)\) is in \(\Pi (G)\) . We show that using port numbering theoretically improves model capability in Section 5.2. We propose CPNGNNs, an example of \(\mathbf{V}\mathbf{V}_{\mathbf{C}}\) - GNNs, in Section 6.  


## 5 GNNs with Distributed Local Algorithms  


In this section, we discuss the relationship between GNNs and distributed local algorithms. Thanks to this relationship, we can elucidate the theoretical properties of GNNs.  


### 5.1 Relationship with Distributed Local Algorithms  


A distributed local algorithm is a distributed algorithm that runs in constant time. More specifically, in a distributed local algorithm, we assume each node has infinite computational resources and decides the output within a constant number of communication rounds with neighboring nodes. In this paper, we show a clear relationship between distributed local algorithms and GNNs for the first time.  


There are several well- known models of distributed local algorithms [10]. Namely, in this paper, we introduce the SB(1), MB(1), and \(\mathbf{V}\mathbf{V}_{\mathbf{C}}(1)\) models. As their names suggest, they correspond to SB- GNNs, MB- GNNs, and \(\mathbf{V}\mathbf{V}_{\mathbf{C}}\) - GNNs, respectively.  


Assumption 3 (Finite Node Features): The number of possible node features is finite.  


Assumption 3 restricts node features be discrete. However, Assumption 3 does include the node degree feature \((\in [\Delta ])\) and node coloring feature \((\in \{0,1\})\) .

<--- Page Split --->
Require: Graph \(G = (V,E,X)\) ; Maximum degree \(\Delta \in \mathbb{Z}^{+}\) ; Weight matrix \(W^{(l)} \in \mathbb{R}^{d_{l + 1} \times (d_{l} + \Delta (d_{l} + 1))} (l = 1, \ldots , L)\) .  


Ensure: Output for the graph problem \(y \in Y^{n}\)  


1: calculate a consistent port numbering \(p\)  


1: calculate a consistent port numbering \(p\)  


2: \(z_{v}^{(1)} \leftarrow x_{v} (\forall v \in V)\)  


3: for \(l = 1, \ldots , L\) do  


4: for \(v \in V\) do  


5: \(z_{v}^{(l + 1)} \leftarrow W^{(l)} \operatorname {CONCAT}(z_{v}^{(l)}, z_{p_{\mathrm{tail}}(v,1)}^{(l)}, p_{n}(v,1), z_{p_{\mathrm{tail}}(v,2)}^{(l)}, p_{n}(v,2), \ldots , z_{p_{\mathrm{tail}}(v, \Delta)}^{(l)}, p_{n}(v, \Delta))\)  


6: \(z_{v}^{(l + 1)} \leftarrow \operatorname {RELU}(z_{v}^{(l + 1)})\)  


7: end for  


8: end for  


9: for \(v \in V\) do  


10: \(z_{v} \leftarrow \operatorname {MULTILAYERPERCEPTRON}(z_{v}^{(L + 1)})\) # calculate the final embedding of a node \(v\) .  


11: \(y_{v} \leftarrow \operatorname {argmax}_{i \in [d_{L + 1}]} z_{v i}\) # output the index of the maximum element.  


12: end for  


13: return \(y\)  


Theorem 1. Let \(\mathcal{L}\) be SB, MB, or \(V V_{C}\) . Under Assumption 3, the set of graph problems that at least one \(\mathcal{L}\) - GNN can solve is the same as the set of graph problems that at least one distributed local algorithm on the \(\mathcal{L}(1)\) model solve.  


All proofs are available in the supplementary materials. In fact, the following stronger properties hold: (i) any \(\mathcal{L}\) - GNN can be simulated by the \(\mathcal{L}(1)\) model and (ii) any distributed local algorithm on \(\mathcal{L}(1)\) model can be simulated by an \(\mathcal{L}\) - GNN. The former is obvious because GNNs communicate with neighboring nodes in \(L\) rounds, where \(L\) is the number of layers. The latter is natural because the definition of \(\mathcal{L}\) - GNNs (Section 3.2 and 4) is intrinsically the same as the definition of the \(\mathcal{L}(1)\) model. Thanks to Theorem 1, we can prove which combinatorial problems GNNs can/cannot solve by using theoretical results on distributed local algorithms.  


### 5.2 Hierarchy of GNNs  


There are obvious inclusion relations among classes of GNNs. Namely, SB- GNNs are a subclass of MB- GNNs, and MB- GNNs are a subclass of \(\mathrm{VV}_{C}\) - GNNs. If a model class \(\mathcal{A}\) is a subset of a model class \(\mathcal{B}\) , the graph problems that \(\mathcal{A}\) solves is a subset of the graph problems that \(\mathcal{B}\) solves. However, it is not obvious whether the proper inclusion property holds or not. Let \(\mathcal{P}_{\mathrm{SB - GNNs}}\) , \(\mathcal{P}_{\mathrm{MB - GNNs}}\) , and \(\mathcal{P}_{\mathrm{VV}_{C} - \mathrm{GNNs}}\) be the sets of graph problems that SB- GNNs, MB- GNNs, and \(\mathrm{VV}_{C}\) - GNNs can solve only with the degree features, respectively. Thanks to the relationship between GNNs and distributed local algorithms, we can show that the proper inclusion properties of these classes hold.  


Theorem 2. \(\mathcal{P}_{\mathrm{SB - GNNs}} \subsetneq \mathcal{P}_{\mathrm{MB - GNNs}} \subsetneq \mathcal{P}_{\mathrm{VV}_{C} - \mathrm{GNNs}}\) .  


An example graph problem that MB- GNNs cannot solve but \(\mathrm{VV}_{C}\) - GNNs can solve is the finding single leaf problem [10]. The input graphs of the problem are star graphs and the ground truth contains only a single leaf node. MB- GNNs cannot solve this problem because for each layer, the embeddings of the leaf nodes are exactly same, and the GNN cannot distinguish these nodes. Therefore, if a GNN includes one leaf node in the output, the other leaf nodes are also included to the output. On the other hand, \(\mathrm{VV}_{C}\) - GNNs can distinguish each leaf node using port numbering and can appropriately output only a single node. We confirm this fact through experiments in the supplementary materials.  


## 6 Most Powerful GNN for Combinatorial Problems

<--- Page Split --->
### 6.1 Consistent Port Numbering Graph Neural Networks (CPNGNNs)  


In this section, we propose the most powerful \(\mathrm{VV}_{C}\) - GNNs, CPNGNNs. The most similar algorithm to CPNGNNs is GraphSAGE [9]. The key differences between GraphSAGE and CPNGNNs are as follows: (i) CPNGNNs use port numbering and (ii) CPNGNNs aggregate features of neighbors by concatenation. We show pseudo code of CPNGNNs in Algorithm 2. Though CPNGNNs are simple, they are the most powerful among \(\mathrm{VV}_{C}\) - GNNs. This claim is supported by Theorem 3, where we do not limit node features to the node degree feature.  


Theorem 3. Let \(\mathcal{P}_{CPNGNNs}\) be the set of graph problems that CPNGNNs can solve and \(\mathcal{P}_{\mathrm{VV}_{C}}\) - GNNs be the set of graph problems that \(\mathrm{VV}_{C}\) - GNNs can solve. Then, under Appsumtion 3, \(\mathcal{P}_{CPNGNNs} = \mathcal{P}_{\mathrm{VV}_{C}}\) - GNNs.  


The advantages of CPNGNNs are twofold: they can solve a strictly wider set of graph problems than existing models (Theorem 2 and 3). There are many distributed local algorithms that can be simulated by CPNGNNs and we can prove that CPNGNNs can solve a variety of combinatorial problems (see Section 6.2).  


### 6.2 Combinatorial Problems that CPNGNNs Can/Cannot Solve  


In Section 5.2, we found that there exist graph problems that certain GNNs can solve but others cannot. However, there remains a question. What kind of graph problems can/cannot GNNs solve? In this paper, we study combinatorial problems, including the minimum dominating set problem, maximum matching problem, and minimum vertex cover problem. If GNNs can solve combinatorial problems, we may automatically obtain new algorithms for combinatorial problems by simply training GNNs. Note that from Theorems 2 and 3, if CPNGNNs cannot solve a graph problem, other GNNs cannot solve the problem. Therefore, it is important to investigate the capability of CPNGNNs to study the limitations of GNNs.  


Minimum Dominating Set Problem. First, we investigate the minimum dominating set problem.  


Theorem 4. The optimal approximation ratio of CPNGNNs for the minimum dominating set problem is \((\Delta +1)\) . In other words, CPNGNNs can solve \((\Delta +1)\) - approximation for the minimum dominating set problem, but for any \(1 \leq \alpha < \Delta +1\) , CPNGNNs cannot solve \(\alpha\) - approximation for the minimum dominating set problem.  


Here, CPNGNNs can solve \(f(\Delta)\) approximation for the minimum dominating set problem means that for all \(\Delta \in \mathbb{Z}^{+}\) , there exists a parameter \(\theta\) such that for all input \(G \in \mathcal{F}(\Delta)\) , \(\{v \in V \mid \mathrm{CPNGNN}_{\theta}(G, v) = 1\}\) forms \(f(\Delta)\) approximation of the minimum dominating set of \(G\) . However, \((\Delta +1)\) - approximation is trivial because it can be achieved by outputting all the nodes. Therefore, Theorem 4 says that any GNN is as bad as the trivial algorithm in the worst case, which is unsatisfactory. This is possibly because we only use the degree information of local nodes, and we may improve the approximation ratio if we use information other than node degree. Interestingly, we can improve the approximation ratio just by using weak 2- coloring as a feature of nodes. A weak 2- coloring is a function \(c: V \to \{0, 1\}\) such that for any node \(v \in V\) , there exists a neighbor \(u \in \mathcal{N}(v)\) such that \(c(v) \neq c(u)\) . Note that any graph has a weak 2- coloring and that we can calculate a weak 2- coloring in linear time by a breadth- first search. In the theorems below, we use not only the degree \(\deg (v)\) but also the color \(c(v)\) as a feature vector of a node \(v \in V\) . There may be many weak 2- colorings of a graph \(G\) . However, the choice of \(c\) is arbitrary.  


Theorem 5. If the feature vector of a node is consisted of the degree and the color of a weak 2- coloring, the optimal approximation ratio of CPNGNNs for the minimum dominating set problem is \((\frac{\Delta + 1}{2})\) . In other words, CPNGNN can solve \((\frac{\Delta + 1}{2})\) - approximation for the minimum dominating set problem, and for any \(1 \leq \alpha < \frac{\Delta + 1}{2}\) , CPNGNN cannot solve \(\alpha\) - approximation for the minimum dominating set problem.  


In the minimum dominating set problem, we cannot improve the approximation ratio by using 2- coloring instead of weak 2- coloring.  


Theorem 6. Even if the feature vector of a node is consisted of the degree and the color of a 2- coloring, for any \(1 \leq \alpha < \frac{\Delta + 1}{2}\) CPNGNNs cannot solve \(\alpha\) - approximation for the minimum dominating set problem.

<--- Page Split --->
Minimum Vertex Cover Problem. Next, we investigate the minimum vertex cover problem.  


Theorem 7. The optimal approximation ratio of CPNGNNs for the minimum vertex cover problem is 2. In other words, CPNGNNs can solve 2- approximation for the minimum vertex cover problem, and for any \(1 \leq \alpha < 2\) , CPNGNNs cannot solve \(\alpha\) - approximation for the minimum vertex cover problem.  


The simple greedy algorithm can solve 2- approximation for the minimum vertex cover problem. However, this result is not trivial because the algorithm that GNNs learn is not a regular algorithm but a distributed local algorithm. The distributed local algorithm for 2- approximation for the minimum vertex cover problem is known but not so simple [2]. This result also says that if one wants to find an approximation algorithm using a machine learning approach with better performance than 2- approximation, they must use a non- GNN model or combine GNNs with other methods (e.g., a search method).  


Maximum Matching Problem. Lastly, we investigate the maximum matching problem. So far, we have only investigated problems on nodes, not edges. We must specify how GNNs output edge labels. Graph edge problems are defined similarly to graph problems, but their solutions are functions \(E \to Y\) . In this paper, we only consider \(Y = \{0,1\}\) and we only use \(\mathrm{VV}_{\mathrm{C}}\) - GNNs for solving graph edge problems. Let \(G \in \mathcal{F}(\Delta)\) be a graph and \(p\) be a port numbering of \(G\) . To solve graph edge problems, GNNs output a vector \(y(v) \in \{0,1\}^{\Delta}\) for each node \(v \in V\) . For each edge \(\{u,v\}\) , GNNs include the edge \(\{u,v\}\) in the output if and only if \(y(u)_i = y(v)_j = 1\) , where \(p(u,i) = (v,j)\) and \(p(v,j) = (u,i)\) . Intuitively, each node outputs "yes" or "no" to each incident edge (i.e., a port) and we include an edge in the output if both ends output "yes" to the edge. As with graph problems, we say a class \(\mathcal{N}\) of GNNs solves a graph edge problem \(\Pi\) if for any \(\Delta \in \mathbb{Z}^{+}\) , there exists a GNN \(N_{\theta} \in \mathcal{N}\) and its parameter \(\theta\) such that for any graph \(G \in \mathcal{F}(\Delta)\) and any consistent port numbering \(p\) of \(G\) , the output \(N_{\theta}(G,p)\) is in \(\Pi (G)\) .  


We investigate the maximum matching problem in detail. In fact, GNNs cannot solve the maximum matching problem at all.  


Theorem 8. For any \(\alpha \in \mathbb{R}^{+}\) , CPNGNNs that cannot solve \(\alpha\) - approximation for the maximum matching problem.  


However, CPNGNNs can approximate the maximum matching problem with weak 2- coloring feature.  


Theorem 9. If the feature vector of a node is consisted of the degree and the color of a weak 2- coloring, the optimal approximation ratio of CPNGNNs for the maximum matching problem is \((\frac{\Delta + 1}{2})\) . In other words, CPNGNNs can solve \((\frac{\Delta + 1}{2})\) - approximation for the maximum matching problem, and for any \(1 \leq \alpha < \frac{\Delta + 1}{2}\) , CPNGNNs cannot solve \(\alpha\) - approximation for the maximum matching problem.  


Furthermore, if we use 2- coloring instead of weak 2- coloring, we can improve the approximation ratio. In fact, it can achieve any approximation ratio. Note that only a bipartite graph has 2- coloring. Therefore, the graph class is implicitly restricted to bipartite graphs in this case.  


Theorem 10. If the feature vector of a node is consisted of the degree and the color of a 2- coloring, for any \(1 < \alpha\) , CPNGNNs can solve \(\alpha\) - approximation for the maximum matching problem.  


## 7 Conclusion  


In this paper, we introduced \(\mathrm{VV}_{\mathrm{C}}\) - GNNs, which are a new class of GNNs, and CPNGNNs, which are an example of \(\mathrm{VV}_{\mathrm{C}}\) - GNNs. We showed that \(\mathrm{VV}_{\mathrm{C}}\) - GNNs have the same ability to solve graph problems as a computational model of distributed local algorithms. With the aid of distributed local

<--- Page Split --->
algorithm theory, we elucidated the approximation ratios of algorithms that CPNGNNs can learn for combinatorial graph problems such as the minimum dominating set problem and the minimum vertex cover problem. This paper is the first to show the approximation ratios of GNNs for combinatorial problems. Moreover, this is a lower bound of approximation ratios for all GNNs. We further showed that adding coloring or weak coloring to a node feature improves these approximation ratios. This indicates that preprocessing and feature engineering theoretically strengthen model capability.  


## Acknowledgments  


This work was supported by JSPS KAKENHI Grant Number 15H01704. MY is supported by the JST PRESTO program JPMJPR165A.  


## References  


[1] Dana Angluin. Local and global properties in networks of processors (extended abstract). In Proceedings of the 12th Annual ACM Symposium on Theory of Computing, pages 82- 93, 1980.  


[2] Matti Åstrand, Patrik Floreén, Valentin Polishchuk, Joel Rybicki, Jukka Suomela, and Jara Uitto. A local 2- approximation algorithm for the vertex cover problem. In Proceedings of 23rd International Symposium on Distributed Computing, DISC 2009, pages 191- 205, 2009.  


[3] Matti Åstrand, Valentin Polishchuk, Joel Rybicki, Jukka Suomela, and Jarua Uitto. Local algorithms in (weakly) coloured graphs. CoRR, abs/1002.0125, 2010.  


[4] Irwan Bello, Hieu Pham, Quoc V. Le, Mohammad Norouzi, and Samy Bengio. Neural combinatorial optimization with reinforcement learning. CoRR, abs/1611.09940, 2016.  


[5] George Cybenko. Approximation by superpositions of a sigmoidal function. MCSS, 2(4):303- 314, 1989.  


[6] Andrzej Czygrinow, Michal Hanckowiak, and Wojciech Wawrzyniak. Fast distributed approximations in planar graphs. In Proceedings of 22nd International Symposium on Distributed Computing, DISC 2008, pages 78- 92, 2008.  


[7] Justin Gilmer, Samuel S. Schoenholz, Patrick F. Riley, Oriol Vinyals, and George E. Dahl. Neural message passing for quantum chemistry. In Proceedings of the 34th International Conference on Machine Learning, ICML 2017, pages 1263- 1272, 2017.  


[8] Marco Gori, Gabriele Monfardini, and Franco Scarselli. A new model for learning in graph domains. In Proceedings of the International Joint Conference on Neural Networks, IJCNN 2005, volume 2, pages 729- 734, 2005.  


[9] William L. Hamilton, Zhitao Ying, and Jure Leskovec. Inductive representation learning on large graphs. In Advances in Neural Information Processing Systems 30: Annual Conference on Neural Information Processing Systems 2017, NIPS 2017, pages 1025- 1035, 2017.  


[10] Lauri Hella, Matti Järvisalo, Antti Kuusisto, Juhana Laurinharju, Tuomo Lempiäinen, Kerkko Luosto, Jukka Suomela, and Jonni Virtema. Weak models of distributed computing, with connections to modal logic. In Proceedings of the ACM Symposium on Principles of Distributed Computing, PODC 2012, pages 185- 194, 2012.  


[11] Elias B. Khalil, Hanjun Dai, Yuyu Zhang, Bistra Dilkina, and Le Song. Learning combinatorial optimization algorithms over graphs. In Advances in Neural Information Processing Systems 30: Annual Conference on Neural Information Processing Systems, 2017, NIPS 2017, pages 6351- 6361, 2017.  


[12] Thomas N. Kipf and Max Welling. Semi- supervised classification with graph convolutional networks. CoRR, abs/1609.02907, 2016.  


[13] Martin Kubisch, Holger Karl, Adam Wolisz, Lizhi Charlie Zhong, and Jan M. Rabaey. Distributed algorithms for transmission power control in wireless sensor networks. In Proceedings of the 2003 IEEE Wireless Communications and Networking, WCNC 2003, pages 558- 563, 2003.

<--- Page Split --->
[14] Christoph Lenzen, Jukka Suomela, and Roger Wattenhofer. Local algorithms: Self- stabilization on speed. In Proceedings of 11th International Symposium on Stabilization, Safety, and Security of Distributed Systems, SSS 2009, pages 17- 34, 2009.  


[15] Christoph Lenzen and Roger Wattenhofer. Leveraging linial's locality limit. In Proceedings of 22nd International Symposium on Distributed Computing, DISC 2008, pages 394- 407, 2008.  


[16] Zhuwen Li, Qifeng Chen, and Vladlen Koltun. Combinatorial optimization with graph convolutional networks and guided tree search. In Advances in Neural Information Processing Systems 31: Annual Conference on Neural Information Processing Systems 2018, NeurIPS 2018, pages 537- 546, 2018.  


[17] Nathan Linial. Locality in distributed graph algorithms. SIAM J. Comput., 21(1):193- 201, 1992.  


[18] Moni Naor and Larry J. Stockmeyer. What can be computed locally? SIAM J. Comput., 24(6):1259- 1277, 1995.  


[19] Huy N. Nguyen and Krzysztof Onak. Constant- time approximation algorithms via local improvements. In Proceedings of the 49th Annual IEEE Symposium on Foundations of Computer Science, FOCS, pages 327- 336, 2008.  


[20] Michal Parnas and Dana Ron. Approximating the minimum vertex cover in sublinear time and a connection to distributed algorithms. Theor. Comput. Sci., 381(1- 3):183- 196, 2007.  


[21] Leonardo Filipe Rodrigues Ribeiro, Pedro H. P. Saverese, and Daniel R. Figueiredo. struc2vec: Learning node representations from structural identity. In Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, KDD 2017, pages 385- 394, 2017.  


[22] Franco Scarselli, Marco Gori, Ah Chung Tsoi, Markus Hagenbuchner, and Gabriele Monfardini. The graph neural network model. IEEE Trans. Neural Networks, 20(1):61- 80, 2009.  


[23] Michael Sejr Schlichtkrull, Thomas N. Kipf, Peter Bloem, Rianne van den Berg, Ivan Titov, and Max Welling. Modeling relational data with graph convolutional networks. CoRR, abs/1703.06103, 2017.  


[24] Jukka Suomela. Survey of local algorithms. ACM Comput. Surv., 45(2):24:1- 24:40, 2013.  


[25] Vijay V. Vazirani. Approximation algorithms. Springer, 2001.  


[26] Petar Velickovic, Guillem Cucurull, Arantxa Casanova, Adriana Romero, Pietro Liò, and Yoshua Bengio. Graph attention networks. In Proceedings of the 6th International Conference on Learning Representations, ICLR 2018, 2018.  


[27] Oriol Vinyals, Meire Fortunato, and Navdeep Jaitly. Pointer networks. In Advances in Neural Information Processing Systems 28: Annual Conference on Neural Information Processing Systems 2015, NIPS 2015, pages 2692- 2700, 2015.  


[28] Mirjam Wattenhofer and Roger Wattenhofer. Distributed weighted matching. In Proceedings of 18th International Symposium on Distributed Computing, DISC 2004, pages 335- 348, 2004.  


[29] Ronald J. Williams. Simple statistical gradient- following algorithms for connectionist reinforcement learning. Mach. Learn., 8(3- 4):229- 256, 1992.  


[30] Keyulu Xu, Weihua Hu, Jure Leskovec, and Stefanie Jegelka. How powerful are graph neural networks? CoRR, abs/1810.00826, 2018.  


[31] Rex Ying, Ruining He, Kaifeng Chen, Pong Eksombatchai, William L. Hamilton, and Jure Leskovec. Graph convolutional neural networks for web- scale recommender systems. In Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, KDD 2018, pages 974- 983, 2018.

<--- Page Split --->
## A Proofs  


Lemma 11 ([24]). If the input graph is degree- bounded and input size is bounded by a constant, each node needs to transmit and process only a constant number of bits.  


Proof of Theorem 1. We prove the case of \(\mathcal{L} = \mathrm{VV}_{\mathrm{C}}\) . The proof for other cases can be done similarly. Let \(\mathcal{P}_{\mathrm{GNNs}}\) be the set of graph problems that at least one \(\mathrm{VV}_{\mathrm{C}}\) - GNN can solve and \(\mathcal{P}_{\mathrm{algo}}\) be the set of graph problems that at least one distributed local algorithm on the \(\mathrm{VV}_{\mathrm{C}}(1)\) model can solve. Theorem 1 says that \(\mathcal{P}_{\mathrm{GNNs}} = \mathcal{P}_{\mathrm{algo}}\) . We now prove the following two lemmas.  


Lemma 12. For any \(\mathrm{VV}_{\mathrm{C}}\) - GNN, there exists a distributed local algorithm on the \(\mathrm{VV}_{\mathrm{C}}(1)\) model that solves the same set of graph problems as the \(\mathrm{VV}_{\mathrm{C}}\) - GNN.  


Lemma 13. For any distributed local algorithm on the \(\mathrm{VV}_{\mathrm{C}}(1)\) model, there exists a \(\mathrm{VV}_{\mathrm{C}}\) - GNN that solves the same set of graph problems as the distributed local algorithm.  


If these lemmas hold, for any \(P\in \mathcal{P}_{\mathrm{GNNs}}\) , there exists a \(\mathrm{VV}_{\mathrm{C}}\) - GNN that solves \(P\) . From Lemma 12, there exists a distributed local algorithm on the \(\mathrm{VV}_{\mathrm{C}}(1)\)  model that solves \(P\) . Therefore, \(P\in \mathcal{P}_{\mathrm{algo}}\) and \(\mathcal{P}_{\mathrm{GNNs}}\subseteq \mathcal{P}_{\mathrm{algo}}\) . Conversely, \(\mathcal{P}_{\mathrm{algo}}\subseteq \mathcal{P}_{\mathrm{GNNs}}\) holds by the same argument. Therefore, \(\mathcal{P}_{\mathrm{algo}} =\) \(\mathcal{P}_{\mathrm{GNNs}}\)  


Proof of Lemma 12: Let \(N\) be an arbitrary \(\mathrm{VV}_{\mathrm{C}}\) - GNN and \(L\) be the number of layers of \(N\) . The inference of \(N\) itself is a distributed local algorithm on the \(\mathrm{VV}_{\mathrm{C}}(1)\) model that communicates with neighboring nodes in \(L\) rounds. Namely, the message from the node \(v\) to its \(i\) - th port in the \(l\) - th communication round is a pair \((z_{v}^{(l)},i)\) , and each node calculates the next message based on the received messages and the function \(f\) . Finally, each node calculates the output from the obtained embedding without communication.  


Proof of Lemma 13: Let \(A\) be an arbitrary distributed local algorithm and \(L\) be the number of communication rounds of \(A\) . Let \(F\) be a set of possible input features. From Assumption 3, the cardinality of \(F\) is finite. Let \(m_{v_{i}}^{(l)}\in \mathbb{R}^{d_{l}}\) be the message that node \(v\) receives from \(i\) - th port in the \(l\) - th communication round and \(s_{v}^{(l)}\in \mathbb{R}^{d_{l}}\) be the internal state of node \(v\) in the \(l\) - th communication round. \(s_{v}^{(1)}\) is the input to node \(v\) (e.g., the degree of \(v\) ). Note that we can assume the dimensions of \(m_{v_{i}}^{(l)}\) and \(s_{v}^{(l)}\) to be the constant \(d_{l}\) without loss of generality by Lemma 11. Let \(g_{j}^{(0)}(s_{v}^{(1)}):F\to \mathbb{R}^{d_{1}}\) be the function that calculates the message to the \(j\) - th port in the first communication round from the degree information. Let \(g_{j}^{(l)}(m_{1}^{(l)},m_{2}^{(l)},\ldots ,m_{\Delta}^{(l)},s^{(l)}):\mathbb{R}^{d_{l}(\Delta +1)}\to \mathbb{R}^{d_{l + 1}}\) be the function that calculates the message to the \(j\) - th port in the \((l + 1)\) - th communication round from the received messages and the internal state in the \(l\) - th communication round \((1\leq l\leq L - 1)\) . Let \(g^{(l)}(m_{1}^{(l)},m_{2}^{(l)},\ldots ,m_{\lambda}^{(l)},s^{(l)}):\mathbb{R}^{d_{l}(\Delta +1)} \to \mathbb{R}^{d_{l + 1}}\) be the function that calculates the internal state in the \((l + 1)\) - th communication round from the received messages and the internal states in the \(l\) - th communication round \((1\leq l\leq L - 1)\) Let \(g^{(L)}(m_{1}^{(L)},m_{2}^{(L)},\ldots ,m_{\Delta}^{(L)},s^{(L)}):\mathbb{R}^{d_{L}(\Delta +1)}\to Y\) be the function that determines the output from the received messages and the internal state in the \(L\) - th communication round. Then, we construct a \(\mathrm{VV}_{\mathrm{C}}\) - GNN that solves the same set of graph problem as \(A\) . Namely, let \(f^{(1)}:\mathbb{R}^{d_{1} + (d_{1} + 1)\Delta}\to \mathbb{R}^{d_{2}(\Delta +1)}\) be  


\[f^{(1)}(z_{v}^{(1)},z_{\mathrm{paul}}^{(1)},p_{\mathrm{n}}(v,1),z_{\mathrm{paul}}^{(1)},p_{\mathrm{n}}(v,2),\ldots ,z_{\mathrm{paul}}^{(1)},p_{\mathrm{n}}(v,\Delta)) =\] \[\mathrm{CONCAT}(g_{1}^{(1)}(g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{(1)},1),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{(1)},\Delta),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{(0)},1),z_{\mathrm{paul}}^{(1)},1),\] \[g_{2}^{(1)}(g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{1},1),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{-1},1),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{pauli}}^{-1},1),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{pul}}^{-1},1),z_{\mathrm{paul}}^{(1)},1),\] \[\ldots ,\] \[g_{\Delta}^{(1)}(g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{\mathrm{1}},1),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{*1},1),g_{\mathrm{paul}}^{(1)}(z_{\mathrm{paul}}^{*1},1),\ldots ,g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{*1},\Delta),z_{\mathrm{paul}}^{(1)},1),\] \[g^{(1)}(g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{*1}),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{*1})\ldots ,g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{-1}),g_{\mathrm{paul}}^{(0)}(z_{\mathrm{paul}}^{-1})\ldots ,z_{\mathrm{paul}}^{(1)},1),\]  


and let \(f^{(l)}:\mathbb{R}^{d_{l}(\Delta +1) + (d_{l}(\Delta +1) + 1)\Delta}\to \mathbb{R}^{d_{l + 1}(\Delta +1)}\) \((2\leq l\leq L - 1)\) be  


\[f^{(l)}(z_{v}^{(l)},z_{\mathrm{paul}}^{(l)},p_{\mathrm{n}}(v,1),z_{\mathrm{paul}}^{(l)},p_{\mathrm{n}}(v,2),\ldots ,z_{\mathrm{paul}}^{-(l)},\mathrm{p}_{\mathrm{n}}(v,\Delta)) =\]

<--- Page Split --->
\[\mathrm{CONCAT}(g_{1}^{(l)}(\pi_{p_{n}(v,1)}^{(l)}(\boldsymbol{z}_{p_{\mathrm{tail}}(v,1)}^{(l)}),\pi_{p_{n}(v,2)}^{(l)}(\boldsymbol{z}_{p_{\mathrm{tail}}(v,2)}^{(l)}),\dots ,\pi_{p_{n}(v,\Delta)}^{(l)}(\boldsymbol{z}_{p_{\mathrm{tail}}(v,\Delta)}^{(l)}),\pi_{\Delta +1}^{(l)}(\boldsymbol{z}_{v}^{(l)})),\] \[\qquad g_{2}^{(l)}(\pi_{p_{n}(v,1)}^{(l)}(\boldsymbol {z}_{p_{\mathrm{tail}}(v,1)}^{(l)}),\pi_{p_{m}(v,2)}^{(l)}(\boldsymbol{z}_{p_{\mathrm{tail}}(v,v)}^{(l)}),\dots ,\pi_{p_{n}(v,\Delta)}^{( l)}(\boldsymbol{z}_{p_{\mathrm{tail}}(v,\Delta)}^{(l)}),\boldsymbol{\pi}_{\Delta +1}^{(l)}(\boldsymbol{z}_{v}^{(l)}))\] \[\qquad \dots ,\] \[\qquad g_{\Delta}^{(l)}(\pi_{p_{n}(v,1)}^{(l)}(\boldsymbol{ z}_{p_{\mathrm{tail}}(v,1)}^{(l)}),\pi_{p_{v}(v,2)}^{(l)}(\boldsymbol{z}_{p_{\mathrm{tail}}(v,\Delta)}^{( l)}),\dots ,\pi_{p_{n}(v,\Delta)}^{(l)}(\pi_{p_{\mathrm{tail}}(v,\Delta)}^{(l)}),\pi_{\Delta +1}^{l}(\boldsymbol{z}_{v}^{(l)}))\] \[\qquad g^{(l)}(\pi_{p_{n}(v,1)}^{(l)}(\boldsymbol{z}_{\mathrm{tail}}(v,1)}^{(l)}),\pi_{p_{n}(v,\Delta)}^{(l)}(\boldsymbol{z}_{p_{\text{tail}}(v,\Delta)}^{(l)}),\dots ,\pi_{p_{n}(v,\Delta)}^{(1)}(\pi_{p_{\mathrm{tail}}(v,\Delta)}^{(l)}),\pi_{ \Delta +1}^{(l)}(\boldsymbol{z}_{v}^{(l)}))\]  


where \(\pi_{i}^{(l)}(h): d_{l}(\Delta + 1) \to d_{l}\) selects the \(i\) - th component from \(h\) ( \(2 \leq l \leq L\) , \(1 \leq i \leq \Delta + 1\) ), namely, \(\pi_{i}^{(l)}(h)_{j} = \mathbf{z}_{d_{l}i + j}\) ( \(1 \leq j \leq d_{l}\) ). Finally, let \(f^{(L)}: \mathbb{R}^{d_{L}(\Delta + 1) + (d_{L}(\Delta + 1) + 1)\Delta} \to Y\) be  


\[f^{(L)}(\mathbf{z}_{v}^{(L)},\mathbf{z}_{p_{\mathrm{tail}}(v,1)}^{(L)},p_{\mathrm{n}}(v,1),\mathbf{z}_{p_{\mathrm{tail}}(v,2)}^{(L)},p_{\mathrm{n}}(v,2),\dots ,\mathbf{z}_{p_{\mathrm{tail}}(v,\Delta)}^{(L)},p_{\mathrm{n}}(v,\Delta)) =\] \[g^{(L)}(\pi_{p_{\mathrm{n}}(v,1)}^{(L)}(\mathbf{z}_{p_{\mathrm{tail}}(v,1)}^{(L)}),\pi_{p_{\mathrm{n}}(v,2)}^{(L)}(\mathbf{z}_{p_{\mathrm{tail}}(v,2)}^{(L)}),\dots ,\pi_{p_{\mathrm{n}}(v,\Delta)}^{(L)}(\mathbf{z}_{p_{\mathrm{tail}}(v,\Delta)}^{(L)}),\pi_{\Delta +1}^{(L)}(\mathbf{z}_{v}^{(L)}))\]  


Intuitively, the embedding of the node \(v\) in the \(l\) - th layer is the concatenation of all the messages that \(v\) sends and the internal state of \(v\) in the \(l\) - th communication round of \(A\) . We now prove that \(\pi_{p_{\mathrm{n}}(v,i)}^{(l)}(\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(l)}) = \mathbf{m}_{v i}^{(l)}\) and \(\pi_{\Delta +1}^{(l)}(\mathbf{z}_{v}^{(l)}) = \mathbf{s}_{v}^{(l)}\) ( \(2 \leq l \leq L\) ) hold by induction. First, \(\mathbf{z}_{v}^{(1)} = \mathbf{s}_{v}^{(1)}\) and \(g_{p_{\mathrm{n}}(v,i)}^{(0)}(\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(1)}) = \mathbf{m}_{v i}^{(1)}\) hold by definition. Therefore,  


\[\pi_{p_{\mathrm{n}}(v,i)}^{(2)}(\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(2)})\] \[\quad = g_{p_{\mathrm{n}}(v,i)}^{(1)}(g_{p_{\mathrm{n}}(p_{\mathrm{tail}}(v,i),1)}^{(0)}(\mathbf{z}_{p_{\mathrm{tail}}(p_{\mathrm{tail}}(v,i),1)}^{(1)}),\dots ,g_{p_{\mathrm{n}}(p_{\mathrm{tail}}(v,i),\Delta)}^{(0)}(\mathbf{z}_{p_{\mathrm{tail}}(p_{\mathrm{tail}},(v,i),\Delta)}^{(1)}),\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(1)})\] \[\quad = g_{p_{\mathrm{tail}}(v,i)}^{(1)}(\mathbf{m}_{p_{\mathrm{tail}}(v,i),1}^{(1)},\mathbf{m}_{p_{\mathrm{tail}}(v,i),2}^{(1)},\dots ,\mathbf{m}_{p_{\mathrm{tail}}(v,i),\Delta}^{(1)},\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(1)})\] \[\quad = \mathbf{m}_{v i}^{(2)}\]  


and  


\[\pi_{\Delta +1}^{(2)}(\mathbf{z}_{v}^{(2)})\] \[\quad = g^{(1)}(g_{p_{\mathrm{n}}(v,1)}^{(0)}(\mathbf{z}_{p_{\mathrm{tail}}(v,1)}^{(1)},g_{p_{\mathrm{n}}(v,2)}^{(0)}(\mathbf{z}_{p_{\mathrm{tail}}(v,2)}^{(1)}),\dots ,g_{p_{\mathrm{n}}(v,\Delta)}^{(0)}(\mathbf{z}_{p_{\mathrm{tail}}(v,\Delta)}^{(1)}),\mathbf{z}_{v}^{(1)})\] \[\quad = g^{(1)}(\mathbf{m}_{v1}^{(1)},\mathbf{m}_{v2}^{(1)},\dots ,\mathbf{m}_{v\Delta}^{(1)},\mathbf{s}_{v}^{(1)})\] \[\quad = \mathbf{s}_{v}^{(2)}\]  


In the induction step, let \(\pi_{p_{\mathrm{n}}(v,i)}^{(k)}(\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(k)}) = \mathbf{m}_{v i}^{(k)}\) and \(\pi_{\Delta +1}^{(k)}(\mathbf{z}_{v}^{(k)}) = \mathbf{s}_{v}^{(k)}\) hold. Then,  


\[\pi_{p_{\mathrm{n}}(v,i)}^{(k + 1)}(\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(k + 1)})\] \[\quad = g_{p_{\mathrm{n}}(v,i)}^{(k)}(\pi_{p_{\mathrm{n}}(p_{\mathrm{tail}}(v,i),1)}^{(k)}(\mathbf{z}_{p_{\mathrm{tail}}(p_{\mathrm{tail}}(v,i,1)}^{(k)},\dots ,\pi_{p_{\mathrm{n}}(p_{\mathrm{tail}}(v,i),\Delta)}^{(k)}(\mathbf{z}_{p_{\mathrm{tail}}(p_{\mathrm{tail}},(v,\Delta)}^{(k)},\pi_{\Delta +1}^{(k)}(\mathbf{z}_{p_{\mathrm{tail}}(v,i)}^{(k)}))\] \[\quad = g_{p_{\mathrm{n}}(v,i)}^{(k)}(\mathbf{m}_{p_{\mathrm{tail}}(v,i),1}^{(k)},\mathbf{m}_{p_{\mathrm{tail}}(v,i),2}^{(k)},\dots ,\mathbf{m}_{p_{\mathrm{tail}}(v,i),\Delta}^{(k)},\mathbf{s}_{p_{\mathrm{tail}}(v,i)}^{(k)})\] \[\quad = \mathbf{m}_{v i}^{(k + 1)}\]  


and  


\[\pi_{\Delta +1}^{(k + 1)}(\mathbf{z}_{v}^{(k + 1)})\] \[\quad = g^{(k)}(\pi_{p_{\mathrm{n}}(v,1)}^{(k)}(\mathbf{z}_{p_{\mathrm{tail}}(v,1)}^{(k)},\pi_{p_{\mathrm{n}}(v,2)}^{(k)}(\mathbf{z}_{p_{\mathrm{tail}}(v,2)}^{(k)},\dots ,\pi_{p_{\mathrm{n}}(v,\Delta)}^{(k)}(\mathbf{z}_{p_{\mathrm{tail}}(v,\Delta)}^{(k)},\pi_{\Delta +1}^{(k)}(\mathbf{z}_{\mathrm{v}}^{(k)}))\] \[\quad = g^{(k)}(\mathbf{m}_{v1}^{(k)},\mathbf{m}_{v2}^{(k)},\dots ,\mathbf{m}_{v\Delta}^{(k)},\mathbf{s}_{v}^{(k)})\] \[\quad = \mathbf{s}_{v}^{(k + 1)}\]  


By induction, \(\pi_{p_{\mathrm{n}}(v,i)}^{(l)}(\mathbf{z}_{p_{i}^{(l)}}^{(l)}) = \mathbf{m}_{v i}^{(l)}\) and \(\pi_{\Delta + 1}^{(l)}(\mathbf{z}_{v}^{(l)}) = \mathbf{s}_{v}^{(\ell)}\) ( \(2 \leq l \leq L\) ) hold. Therefore, the final output of this VVc- GNN is the same as that of \(A\) . \(\square\)  


Lemma 14 ([10]). Let \(\mathcal{P}_{S B(l)}\) , \(\mathcal{P}_{M B(l)}\) , and \(\mathcal{P}_{V V c(l)}\) be the set of graph problems that distributed local algorithms on \(S B(l)\) , \(M B(l)\) , and \(V V c(l)\) models can solve only with the degree features, respectively. Then, \(\mathcal{P}_{S B(l)} \subsetneq \mathcal{P}_{M B(l)} \subsetneq \mathcal{P}_{V V c(l)}\) .

<--- Page Split --->
Proof of Theorem 2. From Theorem 1 and Lemma 14, \(\mathcal{P}_{\mathrm{SB}(1)} = \mathcal{P}_{\mathrm{SB - GNNs}}\subsetneq \mathcal{P}_{\mathrm{MB}(1)} = \mathcal{P}_{\mathrm{MB - GNNs}}\subsetneq\) \(\mathcal{P}_{\mathrm{VVC}(1)} = \mathcal{P}_{\mathrm{VVC - GNNs}}\) holds.  


Lemma 15 ([1, 24]). Let \(A\) be any distributed local algorithm with \(L\) communication rounds, \(G = (V,E)\) and \(G^{\prime} = (V^{\prime},E^{\prime})\) be any graphs, \(p\) and \(p^{\prime}\) be any port numberings of \(G\) and \(G^{\prime}\) , \(X\) and \(X^{\prime}\) be any input to the nodes \(V\) and \(V^{\prime}\) , and \(v\) and \(v^{\prime}\) be any nodes of \(G\) and \(G^{\prime}\) , respectively. If the radius- \(L\) local views of \(v\) and \(v^{\prime}\) are the same, the outputs of \(A\) for \(v\) and \(v^{\prime}\) are the same.  


Proof of Theorem 3. \(\mathcal{P}_{\mathrm{CPNGNNs}}\subseteq \mathcal{P}_{\mathrm{VVC - GNNs}}\) clearly holds because any CPNGNN is a \(\mathrm{VVC - GNN}\) . Now, we prove \(\mathcal{P}_{\mathrm{CPNGNNs}}\supseteq \mathcal{P}_{\mathrm{VVC - GNNs}}\) . We decompose CPNGNNs into two parts. The first part \(\Phi_{\theta}\) corresponds to lines 3- 8 of in Algorithm 2 (i.e., communication round) and the second part \(\Psi_{\theta^{\prime}}\) corresponds to the tenth line of Algorithm 2 (i.e., calculating the final embedding). Namely, \(\Phi_{\theta}(G,X,v) = z_{v}^{(L + 1)}\) and \(\Psi_{\theta^{\prime}}(z_{v}^{(L + 1)}) = z_{v}\) , where \(\theta\) and \(\theta^{\prime}\) are parameters of the network (i.e., \(W^{(l)}\) \((l = 1,2,\ldots ,L)\) and the parameters of MLP).  


Let \(W^{(1)},W^{(2)},\ldots ,W^{(L)}\) be the identity matrices. Let \(G = (V,E)\) and \(G^{\prime} = (V,E)\) be any graphs, \(p\) and \(p^{\prime}\) be any port numberings of \(\boldsymbol{G}\) and \(G^{\prime}\) , \(X\) and \(X^{\prime}\) be input vectors whose elements are non- negative integers, and \(v\) and \(v^{\prime}\) be any nodes of \(G\) and \(C^{\prime}\) , respectively.  


Lemma 16. If the radius- \(L\) local views of \(v\) and \(v^{\prime \prime}\) are the same, \(\Phi_{\theta}(G,X,v) = \Phi_{\theta}(G^{\prime},X^{\prime},v^{\prime})\)  


Proof of Lemma 16. We prove that for any \(v \in V\) , we can reconstruct the radius- \(l\) local view of \(v\) from \(z_{v}^{(l + 1)}\) using mathematical induction. When \(l = 1\) , \(z_{v}^{(2)} = \mathrm{CONCAT}(z_{v}^{(1)},z_{p_{\mathrm{tail}}(v,1)}^{(1)},p_{\mathrm{n}}(v,1),z_{p_{\mathrm{tail}}(v,2)}^{(1)},p_{\mathrm{n}}(v,2),\ldots ,z_{p_{\mathrm{tail}}(v,\Delta)}^{(1)},p_{\mathrm{n}}(v,\Delta))\) . We omit the ReLU function because the vector is always non- negative. The input vector of node \(v\) is \(z_{v}^{(1)}\) . The input vector of the node that sends the message to the \(i\) - th port of node \(v\) is \(z_{p_{\mathrm{tail}}(v,i)}^{(1)}\) , and its port number that sends to the node \(v\) is \(p_{\mathrm{n}}(v,i)\) . Therefore, \(z_{v}^{(2)}\) includes sufficient information on the input vector of node \(v\) , input vectors of neighboring nodes, and port numbering of the incident edges. In the induction step, for any \(v \in V\) , \(z_{v}^{(k + 1)}\) contains sufficient information to reconstruct the radius- \(k\) local view of \(v\) . When \(l = k + 1\) , \(z_{v}^{(k + 2)} = \mathrm{CONCAT}(z_{v}^{(k + 1)},z_{p_{\mathrm{tail}}(v,1)}^{(k + 1)},p_{\mathrm{n}}(v,1),z_{p_{\mathrm{tail}}(w,2)}^{(k + 1)},p_{\mathrm{n}}(v,2),\ldots ,z_{p_{\mathrm{ tail}}(v,\Delta)}^{(k + 1)},p_{\mathrm{n}}(v,\Delta))\) . From the inductive hypothesis, we can reconstruct the radius- \(k\) local view \(\mathcal{T}_{v}\) of node \(v\) . For any \(i\) , we can reconstruct the radius- \(k\) local view \(\mathcal{T}_{i}\) of the node that sends a message to the \(i\) - th port of the node \(v\) . We call this node \(u_{i}\) for the purpose of explanation. Note that we cannot identify which node \(u\) is. We merge all of \(\mathcal{T}_{i}\) with \(\mathcal{T}_{v}\) to construct the radius- \((k + 1)\) local view of node \(v\) . There exists at least one child of the root of \(\mathcal{T}_{i}\) that is compatible when we merge \(\mathcal{T}_{i}\) and \(\mathcal{T}_{v}\) because \(v\) is an adjacent node of \(u_{i}\) . In other words, there exists a child \(c\) of the root of \(\mathcal{T}_{i}\) such that the port numbering between \(c\) and \(u\) is the same as that between \(v\) and \(u\) and the subtree of \(\mathcal{T}_{i}\) where the root is \(c\) is the same as the radius- \((k - 1)\) local view of \(v\) without the subtree where the root is \(v\) . The node \(c\) corresponds to node \(v\) . Note that \(c\) may not be \(v\) itself, but this is irrelevant because the resulting tree is isomorphic. After we merge all \(\mathcal{T}_{i}\) , the resulting tree is the radius- \((k + 1)\) local view of \(v\) . By mathematical induction, for any \(v \in V\) , we can reconstruct the radius- \(l\) local \(\mathrm{view}\) of \(v\) from \(z_{v}^{(l + 1)}\) . Therefore, if the radius- \(L\) local views of \(v\) and \(v^{\prime}\) are same, the outputs \(z_{v}^{(L + 1)}\) and \(z_{v}^{(L + 1)}\) must be the same.  


Furthermore, if the input vectors \(X\) are bounded non- negative integers (i.e., \(X \in (\mathbb{N} \cap [0, \alpha ])^{n \times d_{1}}\) for some \(\alpha \in \mathbb{N}\) ), the output vector \(\Phi_{\theta}(G, X, v)\) consists of bounded non- negative integers (i.e., \(\Phi_{\theta}(G, X, v) \in (\mathbb{N} \cap [0, \beta ])^{d_{L + 1}}\) for some \(\beta \in \mathbb{N}\) ). Let \(N\) be any \(\mathrm{VVC - GNN}\) . From Lemmas 12, there exists a distributed local algorithm \(A\) that solves the same set of graph problems as \(N\) . Let \(f(G, X, v) \in \{0, 1\}^{|Y|}\) represent the one- hot vector of the output of \(A\) . From Lemma 15 and 16, there exists a function \(h(v) : (\mathbb{N} \cap [0, \beta ])^{d_{L + 1}} \to \{0, 1\}^{|Y|}\) such that \(h \circ \Phi_{\theta}(G, X, v) = f(G, X, v)\) . Let \(h' : [0, \beta ]^{d_{L + 1}} \to [0, 1]^{|Y|}\) be a linear interpolation of \(h\) . Because \(h'\) is continuous and bounded, from the universal approximation theorem [5], there exists a parameter \(\theta'\) such that for any \(v \in [0, \beta ]^{d_{L + 1}}\) , \(\| \Psi_{\theta'}(v) - h'(v)\|_{2} < 1 / 3\) . Therefore, the maximum index of \(\Psi_{\theta'}(z_{v}^{(L + 1)})\) is the same as that of \(h(z_{v}^{(L + 1)})\) and the output of this network is the same as that of \(N\) for any input.

<--- Page Split --->
Algorithm 3 Calculating a consistent port numbering  


Require: Graph \(G = (V,E)\)  


Ensure: Consistent port numbering \(p\)  


1: \(c_{v}\gets 0\forall v\in V\)  


2: \(p\leftarrow\) empty dictionary  


3: for \(\{u,v\} \in E\) do  


4: \(c_{u}\gets c_{u} + 1\)  


5: \(c_{v}\gets c_{v} + 1\)  


6: \(p((u,c[u])) = (v,c[v])\)  


7: \(p((v,c[v])) = (u,c[u])\)  


8: end for  


9: return \(p\)  


Lemma 17 ([3, 6, 15]). The optimal approximation ratio of the \(V V_{C}\) model for the minimum dominating set problem is \(\Delta +1\) .  


Lemma 18 ([3]). If inputs contain weak 2- coloring, the optimal approximation ratio of the \(V V_{C}\) model for the minimum dominating set problem is. \(\frac{\Delta + 1}{2}\)  


Lemma 19 ([3]). If inputs contain 2- coloring, the optimal approximation ratio of the \(V V_{C}\) model forthe minimum dominating set problem is \(\frac{\Delta + 1}{2}\)  


Lemma 20 ([2, 6, 15]). The optimal approximation ratio of the \(V V_{C}\) mode for the minimum vertex cover problem is 2.  


Lemma 21 ([3, 6]). The optimal approximation ratio of the \(V V_{C}\) model for the maximum matching problem does not exist.  


Lemma 22 ([3]). If inputs contain weak 2- coloring, the optimal approximation ratio of the \(W V_{C}\) model for the maximum matching problem is \(\frac{\Delta + 1}{2}\)  


Lemma 23 ([3]). For any \(\Delta \geq 1\) and \(\epsilon >0\) , there is a distributed local algorithm on the \(V V_{C}\) model with approximation ratio factor \(1 + \epsilon\) for maximum matching in 2- colored graphs.  


Theorems 4, 5, 6, 7, 8, 9, and 10 immediately follow from Lemmas 17, 18, 19, 20, 21, 22, and 23, respectively, because from Theorems 1 and 3, the set of graph problems that CPNGNNs can solve is the same as that that the \(V V_{C}\) model can.  


## B How to Calculate a Consistent Port Numbering and a Weak 2-Coloring  


A consistent port numbering can be calculated in linear time. We show the pseudo code in Algorithm 3. A weak 2- coloring can be also calculated in linear time by breadth first search. We show the pseudo code in Algorithm 4. Note that if the input graph is bipartite, Algorithm 4 returns a 2- coloring of the input graph.  


## C Experiments  


In this section, we confirm that CPNGNNs can solve a graph problem that existing GNNs cannot through experiments. We use a toy task named finding single leaf [10]. In this problem, the input is a star graph, and the output must be a single leaf of the graph. If the input graph is not a star graph, GNNs may output any subset of nodes. Formally, this graph problem is expressed as follows:  


\[\Pi (G) = \left\{ \begin{array}{ll}\{\{v\} | v\in V,\deg (v) = 1\} & \mathrm{if~}G\mathrm{~is~a~star~graph}\\ 2^{V} & \mathrm{(i.e.,~any~subset~of~}V) & \mathrm{otherwise} \end{array} \right..\]  


No MB- GNN can solve this problem because for any layer, the latent vector in each leaf node is identical and MB- GNNs must output the same decision for all leaf nodes.  


In this experiment, we use a star graph with four nodes: one center node and three leaves used for both training and testing. We use a two- layer CPNGNN that learns the stochastic policy of node

<--- Page Split --->
Algorithm 4 Calculating a weak 2- coloring  


Require: Graph \(G = (V,E)\)  


Ensure: Weak 2- coloring \(c\)  


1: \(f_{v}\gets\) false \(\forall v\in V\)  


2: \(q\gets\) empty queue  


3: \(v_{0}\gets\) an arbitrary node in \(G\)  


4: \(q.\mathrm{push}((v_{0},0))\)  


5: \(f_{v_{0}}\gets\) true  


6: while \(q\) is not empty do  


7: \((v,x)\gets q.\mathrm{front}()\)  


8: \(q.\mathrm{pop}()\)  


9: \(c(v) = x\)  


10: for \(u\in \mathcal{N}(v)\) do  


11: if not \(f_{u}\) then  


12: \(q.\mathrm{push}((u,1 - x))\)  


13: \(f_{u}\gets\) true  


14: end if  


15: end for  


16: end while  


17: return \(c\)  


selection and train the model using the REINFORCE algorithm [29]. If the output selects only one leaf, the reward is 1, and otherwise, the reward is \(- 1\) . We ran 10 trials with different seeds. After 10000 iterations of training, the model solves the finding single leaf problem in all trials. However, we train GCN [12], GraphSAGE [9], and GAT [26] to solve this task, but none of them could solve the finding single leaf problem, as our theory shows. This indicates that the existing GNNs cannot solve such a simple combinatorial problem whereas out proposed model can.

<--- Page Split --->
