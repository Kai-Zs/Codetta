<template>
  <div class="fixed inset-0 pointer-events-none" style="z-index:0">
    <!-- 鲜色渐变底 -->
    <div style="position:absolute;inset:0;background:linear-gradient(135deg,#ede0ff 0%,#dce6ff 40%,#ffe4f0 70%,#e8e0ff 100%)"></div>
    <!-- 45°几何图案层 -->
    <div
      class="bg-pattern-anim"
      style="position:absolute;inset:-100px;opacity:0.22;
             background-image:url(&quot;data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='56'%3E%3Ccircle cx='28' cy='28' r='2.5' fill='%237c3aed'/%3E%3Cpath d='M8 8l12 12M20 8L8 20' stroke='%23a78bfa' stroke-width='1.5' stroke-linecap='round'/%3E%3Cpath d='M48 48l12 12M60 48l-12 12' stroke='%23a78bfa' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E&quot;);
             background-size:56px 56px">
    </div>
  </div>
</template>
