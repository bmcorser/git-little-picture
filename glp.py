#!/usr/bin/env python
import functools
import click
import pygit2
import pydot


def node(colour, git_id):
    return pydot.Node(git_id,
                      style='filled',
                      color=colour)

commit_node = functools.partial(node, '#FF851B')
name_node = functools.partial(node, '#2ECC40')
tree_node = functools.partial(node, '#FFDC00')
blob_node = functools.partial(node, '#7FDBFF')


def recurse_tree(repo, graph, parent, entry):
    'Recurse a Tree, adding to the passed Graph object'
    # import ipdb;ipdb.set_trace()
    git_id = entry.id.hex[:7]
    git_object = repo.get(git_id)
    print(git_id)
    if isinstance(git_object, pygit2.Blob):
        content = blob_node(git_id)
        name = name_node(entry.name)
        graph.add_node(content)
        graph.add_node(name)
        graph.add_edge(pydot.Edge(name, parent))
        graph.add_edge(pydot.Edge(content, name))
        graph.add_node(blob_node(git_id))
        return parent
    if isinstance(git_object, pygit2.Tree):
        node = tree_node(git_id)
        graph.add_node(node)
        graph.add_edge(pydot.Edge(node, parent))
        return recurse_tree(repo, graph, node, git_object)

@click.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.argument('ref', default='HEAD')
def main(repo_path, ref):
    repo = pygit2.Repository(repo_path)
    tree = repo.revparse_single(ref).tree
    import ipdb;ipdb.set_trace()
    graph = pydot.Dot(ref, graph_type='digraph')
    root_node = commit_node(ref)
    graph.add_node(root_node)
    functools.reduce(
        functools.partial(recurse_tree, repo, graph),
        tree,
        root_node,
    )
    # import ipdb;ipdb.set_trace()
    graph.write_svg("{0}.svg".format(ref))

if __name__ == '__main__':
    main()
