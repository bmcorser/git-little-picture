#!/usr/bin/env python
import functools
import click
import pygit2
import pydot

pygit2_constants = {
    pygit2.GIT_OBJ_COMMIT: 'GIT_OBJ_COMMIT',
    pygit2.GIT_OBJ_TREE: 'GIT_OBJ_TREE',
    pygit2.GIT_OBJ_BLOB: 'GIT_OBJ_BLOB',
    pygit2.GIT_OBJ_TAG: 'GIT_OBJ_TAG',
}

def node(prefix, colour, git_id):
    return pydot.Node('"{0}: {1}"'.format(prefix, git_id),
                      style='filled',
                      fontname='courier',
                      color=colour)

commit_node = functools.partial(node, 'commit', '#FF851B')
file_node = functools.partial(node, 'file', '#2ECC40')
tree_node = functools.partial(node, 'tree', '#FFDC00')
blob_node = functools.partial(node, 'blob', '#7FDBFF')


def graph_tree_entries(repo, graph, parent, entry):
    'Recurse a Tree, adding to the passed Graph object'
    git_id = entry.id.hex[:7]
    git_object = repo.get(git_id)
    if isinstance(git_object, pygit2.Blob):
        content = blob_node(git_id)
        name = file_node(entry.name)
        graph.add_node(content)
        graph.add_node(name)
        graph.add_edge(pydot.Edge(parent, name, dir='back'))
        graph.add_edge(pydot.Edge(name, content, dir='back'))
        graph.add_node(blob_node(git_id))
    if isinstance(git_object, pygit2.Tree):
        node = tree_node(entry.name)
        graph.add_node(node)
        graph.add_edge(pydot.Edge(parent, node, dir='back'))
        for entry in git_object:
            graph_tree_entries(repo, graph, node, entry)

@click.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.argument('ref', default='HEAD')
def main(repo_path, ref):
    repo = pygit2.Repository(repo_path)
    tree = repo.revparse_single(ref).tree
    graph = pydot.Dot(graph_type='digraph')
    commit = commit_node(ref)
    graph.add_node(commit)
    root_node = tree_node(tree.id.hex[:7])
    graph.add_node(root_node)
    graph.add_edge(pydot.Edge(commit, root_node, dir='back'))
    for entry in tree:
        graph_tree_entries(repo, graph, root_node, entry)
    graph.write_svg("{0}.svg".format(ref))

if __name__ == '__main__':
    main()
