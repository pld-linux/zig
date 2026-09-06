%define	gitref	ab30a0b9a
%define	snap	20260905
%define	zigver	0.17.0-dev.2018+%{gitref}
#
Summary:	Programming language for maintaining robust, optimal and reusable software
Summary(pl.UTF-8):	Język programowania do tworzenia niezawodnego, optymalnego oprogramowania wielokrotnego użytku
Name:		zig
Version:	0.17.0
Release:	0.%{snap}.1
License:	MIT (compiler), MIT/BSD/LGPL v2.1+ and others (bundled libc sources)
Group:		Development/Languages
Source0:	https://ziglang.org/builds/%{name}-%{zigver}.tar.xz
# Source0-md5:	f44255f821df694f0cb32946f3878076
URL:		https://ziglang.org/
# cmake/Findllvm.cmake accepts one LLVM major only and errors out on anything
# else, so this tracks whichever zig snapshot matches the LLVM PLD ships.
BuildRequires:	clang-devel >= 22.0.0
BuildRequires:	cmake >= 3.15
BuildRequires:	libstdc++-devel
BuildRequires:	lld-devel >= 22.0.0
BuildRequires:	llvm-devel >= 22.0.0
Requires:	%{name}-libs = %{version}-%{release}
# Bootstrap compiles a 222 MB generated zig2.c in one translation unit, peaking
# at ~12 GB in cc1 - far past what a 32-bit address space can hold.
ExclusiveArch:	%{x8664}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Zig is a general-purpose programming language and toolchain for
maintaining robust, optimal and reusable software. It has no hidden
control flow, no hidden memory allocations and no preprocessor or
macros. The toolchain doubles as a drop-in C and C++ cross-compiler.

%description -l pl.UTF-8
Zig to język programowania ogólnego przeznaczenia wraz z zestawem
narzędzi, służący do tworzenia niezawodnego, optymalnego
oprogramowania wielokrotnego użytku. Nie ma w nim ukrytego przepływu
sterowania, ukrytych alokacji pamięci ani preprocesora czy makr.
Zestaw narzędzi działa również jako kompilator skrośny języków C i
C++.

%package libs
Summary:	Zig standard library and bundled libc sources
Summary(pl.UTF-8):	Biblioteka standardowa Ziga oraz dołączone źródła bibliotek C
Group:		Development/Languages
BuildArch:	noarch

%description libs
Zig standard library together with the bundled libc headers and
sources (musl, glibc, mingw-w64, wasi-libc) and compiler-rt that the
compiler needs in order to build and cross-compile programs.

%description libs -l pl.UTF-8
Biblioteka standardowa Ziga wraz z dołączonymi nagłówkami i źródłami
bibliotek C (musl, glibc, mingw-w64, wasi-libc) oraz compiler-rt,
potrzebnymi kompilatorowi do budowania i kompilacji skrośnej
programów.

%prep
%setup -q -n %{name}-%{zigver}

%build
install -d build
cd build
# RelWithDebInfo is the only build type for which CMakeLists.txt does not append
# -Dstrip to the stage3 zig build, so it is what keeps debuginfo.
%cmake .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_C_FLAGS_RELWITHDEBINFO="%{rpmcflags} %{rpmcppflags}" \
	-DCMAKE_CXX_FLAGS_RELWITHDEBINFO="%{rpmcxxflags} %{rpmcppflags}" \
	-DZIG_EXTRA_BUILD_ARGS="--build-id=sha1;-Dno-langref=true" \
	-DZIG_PIE=ON \
	-DZIG_SHARED_LLVM=ON \
	-DZIG_TARGET_MCPU=baseline \
	-DZIG_TARGET_TRIPLE=native \
	-DZIG_VERSION=%{zigver}

%{__make} stage3

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_bindir} $RPM_BUILD_ROOT%{_prefix}/lib

# The cmake install target runs zig with a hardcoded --prefix and ignores
# DESTDIR, so the stage3 tree is copied in by hand instead.
cp -p build/stage3/bin/zig $RPM_BUILD_ROOT%{_bindir}
cp -a build/stage3/lib/zig $RPM_BUILD_ROOT%{_prefix}/lib

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc LICENSE README.md
%attr(755,root,root) %{_bindir}/zig

%files libs
%defattr(644,root,root,755)
%{_prefix}/lib/%{name}
