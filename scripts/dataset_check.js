const fs=require('fs'),vm=require('vm');
const src=fs.readFileSync('G:/hadeeth_id/js/api.js','utf8');
const ctx={console,setTimeout,clearTimeout,TextDecoder,AbortController,fetch,URL,
 location:{href:'https://hadeeth.id/',origin:'https://hadeeth.id',pathname:'/'},
 localStorage:{getItem:()=>null},document:{querySelector:()=>null,querySelectorAll:()=>[],getElementById:()=>null,createElement:()=>({style:{},classList:{add(){},remove(){}}})},navigator:{userAgent:'node'}};
ctx.window=ctx;ctx.globalThis=ctx;vm.createContext(ctx);vm.runInContext(src,ctx);
(async()=>{
 for(const ds of ['native_lidwa','fawazahmed']){
  const p=ctx.HadeethAPI.datasetPrefix(ds);
  const h=await ctx.HadeethAPI.getHadith('bukhari',5,p);
  const ch=await ctx.HadeethAPI.getChapters('bukhari',ds);
  const rows=await ctx.HadeethAPI.getChapterHadiths('bukhari',1,ds);
  const nb=await ctx.HadeethAPI.getHadithNeighbours('bukhari',5,p);
  console.log(ds,'id',h&&h.id,'n',h&&h.hadith_number,'lidwa',h&&h.lidwa_id,
    'ar',h&&String(h.text_ar).slice(0,16),'idtext',h&&String(h.text_id).slice(0,16),
    'chapters',ch.length,'c1',rows.length,'nav',nb&&nb.prev+'/'+nb.next);
 }
 for(const b of ['muslim','malik','darimi']){
  const a=await ctx.HadeethAPI.getChapters(b,'native_lidwa');
  const f=await ctx.HadeethAPI.getChapters(b,'fawazahmed');
  console.log(b,'lidwa chapters',a.length,'fawaz chapters',f.length);
 }
})();
