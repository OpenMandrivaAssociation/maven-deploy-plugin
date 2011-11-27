Name:           maven-deploy-plugin
Version:        2.5
Release:        8
Summary:        Maven Deploy Plugin

Group:          Development/Java
License:        ASL 2.0
URL:            http://maven.apache.org/plugins/maven-deploy-plugin/
#svn export https://svn.apache.org/repos/asf/maven/plugins/tags/maven-deploy-plugin-2.5 maven-deploy-plugin
#tar czf maven-deploy-plugin-2.5.tgz maven-deploy-plugin
Source0:        maven-deploy-plugin-2.5.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch

# Basic stuff
BuildRequires: jpackage-utils
BuildRequires: java-devel >= 0:1.6.0

# Maven and its dependencies
BuildRequires: maven2
BuildRequires: maven-plugin-plugin
BuildRequires: maven-resources-plugin
BuildRequires: maven-compiler-plugin
BuildRequires: maven-install-plugin
BuildRequires: maven-javadoc-plugin
BuildRequires: maven-jar-plugin
BuildRequires: maven-doxia
BuildRequires: maven-doxia-tools
BuildRequires: maven-doxia-sitetools
BuildRequires: maven-surefire-provider-junit
BuildRequires: maven-surefire-maven-plugin
BuildRequires: maven-plugin-cobertura
BuildRequires: maven-archiver
# The following maven packages haven't updated yet
BuildRequires: maven2-plugin-idea
BuildRequires: maven2-plugin-changes
BuildRequires: maven2-plugin-enforcer
BuildRequires: maven2-plugin-invoker

Requires: java
Requires: maven2
Requires: jpackage-utils
Requires(post): jpackage-utils
Requires(postun): jpackage-utils

Provides:       maven2-plugin-deploy = 0:%{version}-%{release}
Obsoletes:      maven2-plugin-deploy <= 0:2.0.8

%description
Uploads the project artifacts to the internal remote repository.

%package javadoc
Group:          Development/Java
Summary:        Javadoc for %{name}
Requires:       jpackage-utils

%description javadoc
API documentation for %{name}.

%prep
%setup -q -n %{name}

%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository

mvn-jpp \
        -e \
        -Dmaven2.jpp.mode=true \
        -Dmaven.test.skip=true \
        -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
        install javadoc:javadoc

%install
rm -rf %{buildroot}

# jars
install -d -m 0755 %{buildroot}%{_javadir}
install -m 644 target/%{name}-%{version}.jar   %{buildroot}%{_javadir}/%{name}-%{version}.jar

(cd %{buildroot}%{_javadir} && for jar in *-%{version}*; \
    do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

%add_to_maven_depmap org.apache.maven.plugins maven-deploy-plugin %{version} JPP maven-deploy-plugin

# poms
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 pom.xml \
    %{buildroot}%{_mavenpomdir}/JPP-%{name}.pom

# javadoc
install -d -m 0755 %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr target/site/api*/* %{buildroot}%{_javadocdir}/%{name}-%{version}/
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}
rm -rf target/site/api*

%post
%update_maven_depmap

%postun
%update_maven_depmap

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{_javadir}/*
%{_mavenpomdir}/*
%{_mavendepmapfragdir}/*

%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}

