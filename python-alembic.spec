%if 0%{?fedora} > 12 || 0%{?rhel} > 6
%global with_python3 1
%endif

%global modname alembic

Name:             python-alembic
Version:          0.3.4
Release:          4%{?dist}
Summary:          Database migration tool for SQLAlchemy

Group:            Development/Libraries
License:          MIT
URL:              http://pypi.python.org/pypi/alembic
Source0:          http://pypi.python.org/packages/source/a/%{modname}/%{modname}-%{version}.tar.gz

BuildArch:        noarch


BuildRequires:    help2man
BuildRequires:    python2-devel
BuildRequires:    python-mako

Requires:         python-mako

# See if we're building for python earlier than 2.7
%if %{?rhel}%{!?rhel:0} >= 6
BuildRequires:    python-sqlalchemy0.7
BuildRequires:    python-argparse
BuildRequires:    python-nose1.1
Requires:         python-sqlalchemy0.7
Requires:         python-argparse
%else
BuildRequires:    python-nose
BuildRequires:    python-sqlalchemy
Requires:         python-sqlalchemy
%endif

%if 0%{?with_python3}
BuildRequires:    python3-devel
BuildRequires:    python-tools
BuildRequires:    python3-sqlalchemy
BuildRequires:    python3-mako
BuildRequires:    python3-nose
%endif


%description
Alembic is a new database migrations tool, written by the author of
`SQLAlchemy <http://www.sqlalchemy.org>`_.  A migrations tool offers the
following functionality:

* Can emit ALTER statements to a database in order to change the structure
of tables and other constructs.
* Provides a system whereby "migration scripts" may be constructed; each script
indicates a particular series of steps that can "upgrade" a target database to
a new version, and optionally a series of steps that can "downgrade"
similarly, doing the same steps in reverse.
* Allows the scripts to execute in some sequential manner.

Documentation and status of Alembic is at http://readthedocs.org/docs/alembic/

%if 0%{?with_python3}
%package -n python3-alembic
Summary:        A database migration tool for SQLAlchemy
Group:          Development/Libraries

Requires:         python3-sqlalchemy
Requires:         python3-mako

%description -n python3-alembic
Alembic is a new database migrations tool, written by the author of
`SQLAlchemy <http://www.sqlalchemy.org>`_.  A migrations tool offers the
following functionality:

* Can emit ALTER statements to a database in order to change the structure
of tables and other constructs.
* Provides a system whereby "migration scripts" may be constructed; each script
indicates a particular series of steps that can "upgrade" a target database to
a new version, and optionally a series of steps that can "downgrade"
similarly, doing the same steps in reverse.
* Allows the scripts to execute in some sequential manner.

Documentation and status of Alembic is at http://readthedocs.org/docs/alembic/
%endif

%prep
%setup -q -n %{modname}-%{version}

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif

# Make sure that epel/rhel picks up the correct version of sqlalchemy
%if %{?rhel}%{!?rhel:0} >= 6
awk 'NR==1{print "import __main__; __main__.__requires__ = __requires__ = [\"sqlalchemy>=0.6\", \"nose>=0.11\"]; import pkg_resources"}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py
%endif



%build
%{__python} setup.py build

%if 0%{?with_python3}
/usr/bin/2to3 -w -n %{py3dir}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif

# Hack around setuptools so we can get access to help strings for help2man
# Credit for this goes to Toshio Kuratomi 
%{__mkdir_p} bin
echo 'python -c "import alembic.config; alembic.config.main()" $*' > bin/alembic
chmod 0755 bin/alembic
help2man --version-string %{version} --no-info -s 1 bin/alembic > alembic.1

%if 0%{?with_python3}
pushd %{py3dir}
%{__mkdir_p} bin
echo 'python3 -c "import alembic.config; alembic.config.main()" $*' > bin/python3-alembic
chmod 0755 bin/python3-alembic
help2man  --version-string %{version} --no-info -s 1 bin/python3-alembic > python3-alembic.1
popd
%endif


%install
install -d -m 0755 %{buildroot}%{_mandir}/man1

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install -O1 --skip-build --root=%{buildroot}
mv %{buildroot}/%{_bindir}/%{modname} %{buildroot}/%{_bindir}/python3-%{modname}
install -m 0644 python3-alembic.1 %{buildroot}%{_mandir}/man1/python3-alembic.1
popd
%endif

%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
install -m 0644 alembic.1 %{buildroot}%{_mandir}/man1/alembic.1

%check
%{__python} setup.py test

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py test
popd
%endif


%files
%doc README.rst LICENSE CHANGES docs
%{python_sitelib}/%{modname}/
%{python_sitelib}/%{modname}-%{version}*
%{_bindir}/%{modname}
%{_mandir}/man1/alembic.1*

%if 0%{?with_python3}
%files -n python3-%{modname}
%doc LICENSE README.rst CHANGES docs
%{python3_sitelib}/%{modname}/
%{python3_sitelib}/%{modname}-%{version}-*
%{_bindir}/python3-%{modname}
%{_mandir}/man1/python3-alembic.1*
%endif


%changelog
* Fri Aug 31 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-4
- Correct %%files entries for the man pages.

* Fri Aug 31 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-3
- Include docs folder in %%doc section.
- Use help2man to build man pages for executables.
- Remove article from summary (cosmetic).
- Add trailing slash to directories in %%files (cosmetic).

* Thu Jul 05 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-2
- Require python-argparse if running on py2.6 or earlier.
- Require the forward-compat python-sqlalchemy on epel.
- Require the forward-compat python-nose on epel.

* Thu Jul 05 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-1
- initial package for Fedora
