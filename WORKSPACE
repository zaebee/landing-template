load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

# Go rules
http_archive(
    name = "io_bazel_rules_go",
    sha256 = "bfc5ce70b9d1634ae54f4e7b495657a18a04e0d596785f672d35d5f505ab491a", # Updated based on Bazel download
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_go/releases/download/v0.40.0/rules_go-v0.40.0.zip",
        "https://github.com/bazelbuild/rules_go/releases/download/v0.40.0/rules_go-v0.40.0.zip",
    ],
)

http_archive(
    name = "bazel_gazelle",
    sha256 = "727f3e4edd96ea20c29e8c2ca9e8d2af724d8c7778e7923a854b2c80952bc405", # Updated based on Bazel download
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/bazel-gazelle/releases/download/v0.30.0/bazel-gazelle-v0.30.0.tar.gz",
        "https://github.com/bazelbuild/bazel-gazelle/releases/download/v0.30.0/bazel-gazelle-v0.30.0.tar.gz",
    ],
)

load("@io_bazel_rules_go//go:deps.bzl", "go_register_toolchains", "go_rules_dependencies")
load("@bazel_gazelle//:deps.bzl", "gazelle_dependencies")

go_rules_dependencies()
go_register_toolchains(version = "1.21.0") # Explicitly set Go version
gazelle_dependencies()

# Node.js rules (for TypeScript, plugins, etc.)
http_archive(
    name = "build_bazel_rules_nodejs", # Renamed for rules_nodejs 4.4.6
    sha256 = "cfc289523cf1594598215901154a6c2515e8bf3671fd708264a6f6aefe02bf39", # Updated from Bazel download for 4.4.6
    # strip_prefix removed
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_nodejs/releases/download/4.4.6/rules_nodejs-4.4.6.tar.gz",
        "https://github.com/bazelbuild/rules_nodejs/releases/download/4.4.6/rules_nodejs-4.4.6.tar.gz",
    ],
)

load("@build_bazel_rules_nodejs//:index.bzl", "npm_install", "node_repositories") # Updated load for 4.4.6

node_repositories(
    package_json = ["//:package.json"], # Assuming root package.json is the main one
)

npm_install(
    name = "npm",
    package_json = "//:package.json",
    package_lock_json = "//:package-lock.json",
)

# Protocol Buffers rules
http_archive(
    name = "rules_proto",
    sha256 = "66bfdf8782796239d3875d37e7de19b1d94301e8972b3cbd2446b332429b4df1", # Updated from Bazel download for 4.0.0
    strip_prefix = "rules_proto-4.0.0",
    urls = [
        "https://github.com/bazelbuild/rules_proto/archive/refs/tags/4.0.0.tar.gz",
    ],
)

load("@rules_proto//proto:repositories.bzl", "rules_proto_dependencies", "rules_proto_toolchains")
rules_proto_dependencies()
rules_proto_toolchains()

# TypeScript rules
# Using npm_install for TypeScript dependencies
# Add a rule like this to your WORKSPACE file:
# npm_install(
# name = "npm",
# package_json = "//:package.json",
# package_lock_json = "//:package-lock.json",
# )
# TypeScript rules
http_archive(
    name = "build_bazel_rules_typescript",
    sha256 = "b9849202a0820a85597093f118031cd877bbbe0092a390979164a0301886422e", # For rules_typescript 0.25.0
    strip_prefix = "rules_typescript-0.25.0",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_typescript/releases/download/0.25.0/rules_typescript-0.25.0.tar.gz",
        "https://github.com/bazelbuild/rules_typescript/releases/download/0.25.0/rules_typescript-0.25.0.tar.gz",
    ],
)

load("@build_bazel_rules_typescript//ts:deps.bzl", "ts_setup_workspace") # This load might change for older version

ts_setup_workspace()

# Placeholder for how protoc-gen-ts is integrated.
# We will use the "npm" dependency for the plugin itself,
# and might use a genrule or a custom macro for the proto compilation.
