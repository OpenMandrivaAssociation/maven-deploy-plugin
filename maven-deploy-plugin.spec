Name:		maven-deploy-plugin
Version:	3.2.0
Release:	1
Summary:	Deploys project artifacts to a remote repository
Group:		Development/Java
License:	Apache-2.0
URL:		https://maven.apache.org/plugins/maven-deploy-plugin/
Source0:	https://github.com/apache/maven-deploy-plugin/archive/refs/tags/maven-deploy-plugin-%{version}.tar.gz#/maven-deploy-plugin-%{version}.tar.gz
# The tag has no license file. This copy is in git, so the build does not
# download it.
Source1:	LICENSE-2.0.txt
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	maven
BuildRequires:	maven-components >= 3.10.0
BuildRequires:	java-current-devel
# Generates META-INF/maven/plugin.xml. The separate annotations package
# conflicts with maven-components on the same index file.
BuildRequires:	maven-plugin-tools
BuildRequires:	mvn(org.apache.maven.plugins:maven-plugin-plugin)
# plexus-xml is not packaged. ReaderFactory and WriterFactory are not in
# plexus-utils 3.6.2; XmlStreamReader and XmlStreamWriter are.
BuildRequires:	mvn(org.codehaus.plexus:plexus-utils)
BuildRequires:	plexus-utils >= 3.6.2
Requires:	plexus-utils >= 3.6.2
BuildRequires:	mvn(org.apache.maven.resolver:maven-resolver-util)
BuildRequires:	mvn(org.apache.maven:maven-plugin-api)
BuildRequires:	mvn(org.apache.maven:maven-core)
BuildRequires:	mvn(org.apache.maven:maven-model)
BuildRequires:	mvn(org.apache.maven:maven-artifact)
BuildRequires:	mvn(org.apache.maven.resolver:maven-resolver-api)
BuildRequires:	mvn(javax.inject:javax.inject)
# javax.inject and jakarta-inject both provide this coordinate.
BuildRequires:	javax.inject >= 1-2
Requires:	javax.inject >= 1-2
BuildRequires:	mvn(org.slf4j:slf4j-api)
BuildRequires:	mvn(org.apache.maven.plugin-tools:maven-plugin-annotations)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

Obsoletes:	maven2-plugin-deploy <= 0:2.0.8
Provides:	maven2-plugin-deploy = %{EVRD}
Obsoletes:	maven-deploy-plugin-javadoc < %{EVRD}

%description
Deploys the project's artifacts to a remote repository. 3.2.0 caches
the reactor scan and backports checks on the POM it deploys. 4.0.0 is
still a beta, so this package stays on 3.2.0. Tests need JUnit
Jupiter, so they are not run.

%prep
%autosetup -n maven-deploy-plugin-maven-deploy-plugin-%{version}
rm -rf src/test src/it .github
cp -p %{SOURCE1} LICENSE
python - <<'PY'
from pathlib import Path
path = Path("src/main/java/org/apache/maven/plugins/deploy/DeployFileMojo.java")
text = path.read_text(encoding="utf-8")
text = text.replace(
    "import org.codehaus.plexus.util.xml.ReaderFactory;\n",
    "import org.codehaus.plexus.util.xml.XmlStreamReader;\n",
)
text = text.replace(
    "import org.codehaus.plexus.util.xml.WriterFactory;\n",
    "import org.codehaus.plexus.util.xml.XmlStreamWriter;\n",
)
text = text.replace("ReaderFactory.newXmlReader(", "new XmlStreamReader(")
text = text.replace("WriterFactory.newXmlWriter(", "new XmlStreamWriter(")
path.write_text(text, encoding="utf-8")
PY
python - <<'PY'
import xml.etree.ElementTree as ET
NS = "http://maven.apache.org/POM/4.0.0"
ET.register_namespace("", NS)

def tag(name):
    return "{" + NS + "}" + name

def add(parent, name, text):
    node = ET.SubElement(parent, tag(name))
    node.text = text
    return node

root = ET.Element(tag("project"))
add(root, "modelVersion", "4.0.0")
add(root, "groupId", "org.apache.maven.plugins")
add(root, "artifactId", "maven-deploy-plugin")
add(root, "version", "%{version}")
add(root, "packaging", "maven-plugin")
add(root, "name", "Apache Maven Deploy Plugin")
props = ET.SubElement(root, tag("properties"))
add(props, "maven.compiler.release", "8")
add(props, "project.build.sourceEncoding", "UTF-8")
deps = ET.SubElement(root, tag("dependencies"))
items = (
    ("org.codehaus.plexus", "plexus-utils", "3.6.2", None),
    ("org.apache.maven.resolver", "maven-resolver-util", "2.0.24", None),
    ("org.apache.maven", "maven-plugin-api", "3.10.0", "provided"),
    ("org.apache.maven", "maven-core", "3.10.0", "provided"),
    ("org.apache.maven", "maven-model", "3.10.0", "provided"),
    ("org.apache.maven", "maven-artifact", "3.10.0", "provided"),
    ("org.apache.maven.resolver", "maven-resolver-api", "2.0.24", "provided"),
    ("javax.inject", "javax.inject", "1", "provided"),
    ("org.slf4j", "slf4j-api", "1.7.36", "provided"),
    ("org.apache.maven.plugin-tools", "maven-plugin-annotations", "3.15.2", "provided"),
)
for group, artifact, version, scope in items:
    dep = ET.SubElement(deps, tag("dependency"))
    add(dep, "groupId", group)
    add(dep, "artifactId", artifact)
    add(dep, "version", version)
    if scope:
        add(dep, "scope", scope)
build = ET.SubElement(root, tag("build"))
plugins = ET.SubElement(build, tag("plugins"))
plugin = ET.SubElement(plugins, tag("plugin"))
add(plugin, "groupId", "org.apache.maven.plugins")
add(plugin, "artifactId", "maven-plugin-plugin")
# The lifecycle binding asks for 3.15.1. The packaged plugin is 3.16.0.
add(plugin, "version", "3.16.0")
ET.ElementTree(root).write("pom.xml", encoding="utf-8", xml_declaration=True)
PY

%files -f .mfiles
%doc LICENSE README.md
