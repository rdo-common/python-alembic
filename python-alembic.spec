%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2:        %global __python2 /usr/bin/python2}
%{!?python2_sitelib:  %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%if 0%{?fedora}
%global with_python3 1
%endif

%global modname alembic

Name:             python-alembic
Version:          0.9.7
Release:          2%{?dist}
Summary:          Database migration tool for SQLAlchemy

Group:            Development/Libraries
License:          MIT
URL:              https://pypi.io/project/alembic
Source0:          https://pypi.io/packages/source/a/%{modname}/%{modname}-%{version}.tar.gz

BuildArch:        noarch


BuildRequires:    help2man
BuildRequires:    python2-devel
BuildRequires:    python-mako
BuildRequires:    python-setuptools
BuildRequires:    python-mock
BuildRequires:    python-dateutil
BuildRequires:    python-editor
BuildRequires:    python2-pytest

# See if we're building for python earlier than 2.7
%if 0%{?rhel} && 0%{?rhel} <= 6
BuildRequires:    python-sqlalchemy0.7 >= 0.7.4
BuildRequires:    python-argparse
BuildRequires:    python-nose1.1
%else
BuildRequires:    python-nose
BuildRequires:    python-sqlalchemy >= 0.7.4
%endif

# Just for the tests
BuildRequires:    python-psycopg2
BuildRequires:    MySQL-python

%if 0%{?with_python3}
BuildRequires:    python3-devel
BuildRequires:    python-tools
BuildRequires:    python3-sqlalchemy >= 0.7.4
BuildRequires:    python3-mako
BuildRequires:    python3-nose
BuildRequires:    python3-setuptools
BuildRequires:    python3-mock
BuildRequires:    python3-dateutil
BuildRequires:    python3-editor
BuildRequires:    python3-pytest
%endif


%global _description\
Alembic is a new database migrations tool, written by the author of\
SQLAlchemy.  A migrations tool offers the following functionality:\
\
* Can emit ALTER statements to a database in order to change the structure\
  of tables and other constructs.\
* Provides a system whereby "migration scripts" may be constructed; each script\
  indicates a particular series of steps that can "upgrade" a target database\
  to a new version, and optionally a series of steps that can "downgrade"\
  similarly, doing the same steps in reverse.\
* Allows the scripts to execute in some sequential manner.\
\
Documentation and status of Alembic is at http://readthedocs.org/docs/alembic/

%description %_description

%package -n python2-alembic
Summary:          %summary

# See if we're building for python earlier than 2.7
%if 0%{?rhel} && 0%{?rhel} <= 6
Requires:         python-sqlalchemy0.7 >= 0.7.4
Requires:         python-argparse
%else
Requires:         python-sqlalchemy >= 0.7.4
%endif

Requires:         python-editor
Requires:         python-dateutil
Requires:         python-setuptools
Requires:         python-mako
%{?python_provide:%python_provide python2-alembic}

%description -n python2-alembic %_description

%if 0%{?with_python3}
%package -n python3-alembic
Summary:          %summary

Requires:         python3-sqlalchemy >= 0.7.4
Requires:         python3-mako
Requires:         python3-setuptools
Requires:         python3-editor
Requires:         python3-dateutil
%{?python_provide:%python_provide python3-alembic}

%description -n python3-alembic %_description
%endif

%prep
%setup -q -n %{modname}-%{version}

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}
%endif

# Make sure that epel/rhel picks up the correct version of sqlalchemy
%if 0%{?rhel} && 0%{?rhel} <= 6
awk 'NR==1{print "import __main__; __main__.__requires__ = __requires__ = [\"sqlalchemy>=0.6\", \"nose>=0.11\"]; import pkg_resources"}1' setup.py > setup.py.tmp
mv setup.py.tmp setup.py
%endif

%build
%{__python2} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif

# Hack around setuptools so we can get access to help strings for help2man
# Credit for this goes to Toshio Kuratomi
%if 0%{?rhel} && 0%{?rhel} <= 6
%else
%{__mkdir_p} bin
echo 'python2 -c "import alembic.config; alembic.config.main()" $*' > bin/python2-alembic
chmod 0755 bin/python2-alembic
help2man --version-string %{version} --no-info -s 1 bin/python2-alembic > python2-alembic.1
%endif

%if 0%{?with_python3}
pushd %{py3dir}
%{__mkdir_p} bin
echo 'python3 -c "import alembic.config; alembic.config.main()" $*' > bin/alembic
chmod 0755 bin/alembic
help2man --version-string %{version} --no-info -s 1 bin/alembic > alembic.1
popd
%endif


%install

install -d -m 0755 %{buildroot}%{_mandir}/man1

%{__python2} setup.py install -O1 --skip-build --root=%{buildroot}
mv bin/python2-%{modname} %{buildroot}/%{_bindir}/python2-%{modname}
install -m 0644 python2-alembic.1 %{buildroot}%{_mandir}/man1/python2-alembic.1

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install --skip-build --root=%{buildroot}
install -m 0644 alembic.1 %{buildroot}%{_mandir}/man1/alembic.1
popd
%endif

%if 0%{?rhel} && 0%{?rhel} <= 6
# Modify /usr/bin/alembic to require SQLAlchemy>=0.6
# Hacky but setuptools only creates this file after setup.py install is run :-(
# Root cause is that setuptools doesn't recurse the requirements when it processes
# the __requires__.  It waits until pkg_resources.require('MODULE') is called.
# Since that isn't done in the entrypoints script, we need to specify the dependency
# on a specific SQLAlchemy version explicitly.
sed -i -e "s|__requires__ = 'alembic==0.4.2'|__requires__ = ['alembic==0.4.2', 'SQLAlchemy>=0.6']|" %{buildroot}%{_bindir}/python2-%{modname}
%endif

%check
%{__python2} setup.py test

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py test
popd
%endif


%files -n python2-alembic
%doc README.rst LICENSE CHANGES docs
%{python2_sitelib}/%{modname}/
%{python2_sitelib}/%{modname}-%{version}*
%{_bindir}/python2-%{modname}

%if 0%{?rhel} && 0%{?rhel} <= 6
%else
%{_mandir}/man1/python2-alembic.1*
%endif

%if 0%{?with_python3}
%files -n python3-%{modname}
%doc LICENSE README.rst CHANGES docs
%{python3_sitelib}/%{modname}/
%{python3_sitelib}/%{modname}-%{version}-*
%{_bindir}/%{modname}
%{_mandir}/man1/alembic.1*
%endif


%changelog
* Sat Jan 27 2018 Ralph Bean <rbean@redhat.com> - 0.9.7-2
- The python3-alembic package now provides the alembic executable.

* Thu Jan 18 2018 Ralph Bean <rbean@redhat.com> - 0.9.7-1
- new version
- New dependency on python-dateutil.

* Tue Aug 08 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 0.9.1-3
- Python 2 binary package renamed to python2-alembic
  See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Mar 02 2017 Ralph Bean <rbean@redhat.com> - 0.9.1-1
- new version

* Wed Mar 01 2017 Ralph Bean <rbean@redhat.com> - 0.9.0-1
- new version

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 17 2017 Ralph Bean <rbean@redhat.com> - 0.8.10-1
- new version

* Tue Dec 27 2016 Kevin Fenzi <kevin@scrye.com> - 0.8.9-1
- Update to 0.8.9. Fixes bug #1400111

* Mon Dec 19 2016 Miro Hrončok <mhroncok@redhat.com> - 0.8.8-2
- Rebuild for Python 3.6

* Sat Sep 17 2016 Kevin Fenzi <kevin@scrye.com> - 0.8.8-1
- Update to 0.8.8. Fixes bug #1376235

* Wed Jul 27 2016 Ralph Bean <rbean@redhat.com> - 0.8.7-1
- new version

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.6-2
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Fri Apr 15 2016 Ralph Bean <rbean@redhat.com> - 0.8.6-1
- new version

* Tue Mar 29 2016 Ralph Bean <rbean@redhat.com> - 0.8.5-1
- new version

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.8.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 24 2015 Ralph Bean <rbean@redhat.com> - 0.8.3-3
- Add requirement on python-editor.

* Tue Nov 10 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.3-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Sat Oct 17 2015 Ralph Bean <rbean@redhat.com> - 0.8.3-1
- new version

* Wed Aug 26 2015 Ralph Bean <rbean@redhat.com> - 0.8.2-1
- new version

* Fri Jul 10 2015 Ralph Bean <rbean@redhat.com> - 0.7.6-3
- Disable tests until sqlalchemy-1.1 is out.  There's a bug against
  MS sql DBs (likely won't affect us).

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 06 2015 Ralph Bean <rbean@redhat.com> - 0.7.6-1
- new version

* Mon Mar 16 2015 Ralph Bean <rbean@redhat.com> - 0.7.4-2
- Merge in epel7 compat changes to the spec file.
- Drop patch for epel7, no longer needed with modern upstream.

* Sat Feb 21 2015 Ralph Bean <rbean@redhat.com> - 0.7.4-1
- new version
- No longer using 2to3.

* Wed Aug 20 2014 Ralph Bean <rbean@redhat.com> - 0.6.6-1
- Latest upstream.
- Modernized python macros.
- Re-enabled python3 tests.
- Cleaned up the description formatting.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue May 27 2014 Kalev Lember <kalevlember@gmail.com> - 0.6.5-2
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Tue May 06 2014 Ralph Bean <rbean@redhat.com> - 0.6.5-1
- Latest upstream.

* Tue Feb 04 2014 Ralph Bean <rbean@redhat.com> - 0.6.3-1
- Latest upstream.

* Tue Jan 28 2014 Ralph Bean <rbean@redhat.com> - 0.6.2-2
- Simplify some nested conditionals.
- Attempt a better rhel conditional.
- Added buildtime dep on python-mock for the test suite.

* Tue Jan 28 2014 Ralph Bean <rbean@redhat.com> - 0.6.2-1
- Latest upstream.

* Mon Jul 29 2013 Ralph Bean <rbean@redhat.com> - 0.5.0-2
- Add forgotten dependency on python-setuptools.
  https://bugzilla.redhat.com/show_bug.cgi?id=989016

* Wed May 29 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 0.4.2-2
- Workaround setuptools to load the correct SQLAlchemy version for
  the alembic script. https://bugzilla.redhat.com/show_bug.cgi?id=968404

* Wed Apr 10 2013 Ralph Bean <rbean@redhat.com> - 0.5.0-1
- Update to 0.5.0

* Thu Mar 14 2013 Pádraig Brady <pbrady@redhat.com> - 0.4.2-1
- Update to 0.4.2

* Fri Feb 22 2013 Ralph Bean <rbean@redhat.com> - 0.3.4-11
- Rebuilt again for good measure.
- Disabled python3 tests.. they started failing in rawhide.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.4-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Sep 12 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-9
- Require at least sqlalchemy 0.7.4.

* Wed Sep 12 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-8
- Don't install manpages if they don't exist.

* Wed Sep 12 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-7
- Stop trying to build man pages for el6.

* Wed Sep 12 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-6
- Typofix.

* Wed Sep 12 2012 Ralph Bean <rbean@redhat.com> - 0.3.4-5
- Accomodate older help2man on epel.

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
