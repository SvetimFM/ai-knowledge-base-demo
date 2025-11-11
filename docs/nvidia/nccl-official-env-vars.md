# NVIDIA NCCL Documentation: Nccl - Env Vars

**Source**: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/env.html
**Converted**: 2025-11-10
**Version**: NCCL 2.28.6

---

<div class="wy-grid-for-nav">

<div class="wy-side-scroll">

<div class="wy-side-nav-search">

[NCCL](index.html)

<div class="version">

[2.28](https://docs.nvidia.com/deeplearning/sdk/nccl-archived/index.html)

</div>

<div role="search">

</div>

</div>

<div class="wy-menu wy-menu-vertical" data-spy="affix" role="navigation" aria-label="main navigation">

  - [Overview of NCCL](overview.html)
  - [Setup](setup.html)
  - [Using NCCL](usage.html)
      - [Creating a Communicator](usage/communicators.html)
          - [Creating a communicator with options](usage/communicators.html#creating-a-communicator-with-options)
          - [Creating a communicator using multiple ncclUniqueIds](usage/communicators.html#creating-a-communicator-using-multiple-nccluniqueids)
          - [Shrinking a communicator](usage/communicators.html#shrinking-a-communicator)
          - [Creating more communicators](usage/communicators.html#creating-more-communicators)
          - [Using multiple NCCL communicators concurrently](usage/communicators.html#using-multiple-nccl-communicators-concurrently)
          - [Finalizing a communicator](usage/communicators.html#finalizing-a-communicator)
          - [Destroying a communicator](usage/communicators.html#destroying-a-communicator)
      - [Error handling and communicator abort](usage/communicators.html#error-handling-and-communicator-abort)
          - [Asynchronous errors and error handling](usage/communicators.html#asynchronous-errors-and-error-handling)
      - [Fault Tolerance](usage/communicators.html#fault-tolerance)
      - [Quality of Service](usage/communicators.html#quality-of-service)
      - [Collective Operations](usage/collectives.html)
          - [AllReduce](usage/collectives.html#allreduce)
          - [Broadcast](usage/collectives.html#broadcast)
          - [Reduce](usage/collectives.html#reduce)
          - [AllGather](usage/collectives.html#allgather)
          - [ReduceScatter](usage/collectives.html#reducescatter)
          - [AlltoAll](usage/collectives.html#alltoall)
          - [Gather](usage/collectives.html#gather)
          - [Scatter](usage/collectives.html#scatter)
      - [Data Pointers](usage/data.html)
      - [CUDA Stream Semantics](usage/streams.html)
          - [Mixing Multiple Streams within the same ncclGroupStart/End() group](usage/streams.html#mixing-multiple-streams-within-the-same-ncclgroupstart-end-group)
      - [Group Calls](usage/groups.html)
          - [Management Of Multiple GPUs From One Thread](usage/groups.html#management-of-multiple-gpus-from-one-thread)
          - [Aggregated Operations (2.2 and later)](usage/groups.html#aggregated-operations-2-2-and-later)
          - [Group Operation Ordering Semantics](usage/groups.html#group-operation-ordering-semantics)
          - [Nonblocking Group Operation](usage/groups.html#nonblocking-group-operation)
      - [Point-to-point communication](usage/p2p.html)
          - [Sendrecv](usage/p2p.html#sendrecv)
          - [One-to-all (scatter)](usage/p2p.html#one-to-all-scatter)
          - [All-to-one (gather)](usage/p2p.html#all-to-one-gather)
          - [All-to-all](usage/p2p.html#all-to-all)
          - [Neighbor exchange](usage/p2p.html#neighbor-exchange)
      - [Thread Safety](usage/threadsafety.html)
      - [In-place Operations](usage/inplace.html)
      - [Using NCCL with CUDA Graphs](usage/cudagraph.html)
      - [User Buffer Registration](usage/bufferreg.html)
          - [NVLink Sharp Buffer Registration](usage/bufferreg.html#nvlink-sharp-buffer-registration)
          - [IB Sharp Buffer Registration](usage/bufferreg.html#ib-sharp-buffer-registration)
          - [General Buffer Registration](usage/bufferreg.html#general-buffer-registration)
          - [Buffer Registration and PXN](usage/bufferreg.html#buffer-registration-and-pxn)
          - [Memory Allocator](usage/bufferreg.html#memory-allocator)
          - [Window Registration](usage/bufferreg.html#window-registration)
          - [Zero-CTA Optimization](usage/bufferreg.html#zero-cta-optimization)
      - [Device-Initiated Communication](usage/deviceapi.html)
          - [Device API](usage/deviceapi.html#device-api)
          - [Host-Side Setup](usage/deviceapi.html#host-side-setup)
          - [Simple LSA Kernel](usage/deviceapi.html#simple-lsa-kernel)
          - [Multimem Device Kernel](usage/deviceapi.html#multimem-device-kernel)
          - [Thread Groups](usage/deviceapi.html#thread-groups)
          - [Teams](usage/deviceapi.html#teams)
          - [GIN Device Kernel](usage/deviceapi.html#gin-device-kernel)
  - [NCCL API](api.html)
      - [Communicator Creation and Management Functions](api/comms.html)
          - [ncclGetLastError](api/comms.html#ncclgetlasterror)
          - [ncclGetErrorString](api/comms.html#ncclgeterrorstring)
          - [ncclGetVersion](api/comms.html#ncclgetversion)
          - [ncclGetUniqueId](api/comms.html#ncclgetuniqueid)
          - [ncclCommInitRank](api/comms.html#ncclcomminitrank)
          - [ncclCommInitAll](api/comms.html#ncclcomminitall)
          - [ncclCommInitRankConfig](api/comms.html#ncclcomminitrankconfig)
          - [ncclCommInitRankScalable](api/comms.html#ncclcomminitrankscalable)
          - [ncclCommSplit](api/comms.html#ncclcommsplit)
          - [ncclCommShrink](api/comms.html#ncclcommshrink)
          - [ncclCommFinalize](api/comms.html#ncclcommfinalize)
          - [ncclCommRevoke](api/comms.html#ncclcommrevoke)
          - [ncclCommDestroy](api/comms.html#ncclcommdestroy)
          - [ncclCommAbort](api/comms.html#ncclcommabort)
          - [ncclCommGetAsyncError](api/comms.html#ncclcommgetasyncerror)
          - [ncclCommCount](api/comms.html#ncclcommcount)
          - [ncclCommCuDevice](api/comms.html#ncclcommcudevice)
          - [ncclCommUserRank](api/comms.html#ncclcommuserrank)
          - [ncclCommRegister](api/comms.html#ncclcommregister)
          - [ncclCommDeregister](api/comms.html#ncclcommderegister)
          - [ncclCommWindowRegister](api/comms.html#ncclcommwindowregister)
          - [ncclCommWindowDeregister](api/comms.html#ncclcommwindowderegister)
          - [ncclMemAlloc](api/comms.html#ncclmemalloc)
          - [ncclMemFree](api/comms.html#ncclmemfree)
      - [Collective Communication Functions](api/colls.html)
          - [ncclAllReduce](api/colls.html#ncclallreduce)
          - [ncclBroadcast](api/colls.html#ncclbroadcast)
          - [ncclReduce](api/colls.html#ncclreduce)
          - [ncclAllGather](api/colls.html#ncclallgather)
          - [ncclReduceScatter](api/colls.html#ncclreducescatter)
          - [ncclAlltoAll](api/colls.html#ncclalltoall)
          - [ncclGather](api/colls.html#ncclgather)
          - [ncclScatter](api/colls.html#ncclscatter)
      - [Group Calls](api/group.html)
          - [ncclGroupStart](api/group.html#ncclgroupstart)
          - [ncclGroupEnd](api/group.html#ncclgroupend)
          - [ncclGroupSimulateEnd](api/group.html#ncclgroupsimulateend)
      - [Point To Point Communication Functions](api/p2p.html)
          - [ncclSend](api/p2p.html#ncclsend)
          - [ncclRecv](api/p2p.html#ncclrecv)
      - [Types](api/types.html)
          - [ncclComm\_t](api/types.html#ncclcomm-t)
          - [ncclResult\_t](api/types.html#ncclresult-t)
          - [ncclDataType\_t](api/types.html#nccldatatype-t)
          - [ncclRedOp\_t](api/types.html#ncclredop-t)
          - [ncclScalarResidence\_t](api/types.html#ncclscalarresidence-t)
          - [ncclConfig\_t](api/types.html#ncclconfig-t)
          - [ncclSimInfo\_t](api/types.html#ncclsiminfo-t)
          - [ncclWindow\_t](api/types.html#ncclwindow-t)
      - [User Defined Reduction Operators](api/ops.html)
          - [ncclRedOpCreatePreMulSum](api/ops.html#ncclredopcreatepremulsum)
          - [ncclRedOpDestroy](api/ops.html#ncclredopdestroy)
      - [NCCL API Supported Flags](api/flags.html)
          - [Window Registration Flags](api/flags.html#window-registration-flags)
          - [NCCL Communicator CTA Policy Flags](api/flags.html#nccl-communicator-cta-policy-flags)
          - [Communicator Shrink Flags](api/flags.html#communicator-shrink-flags)
      - [Device API](api/device.html)
          - [Host-Side Setup](api/device.html#host-side-setup)
              - [ncclDevComm](api/device.html#nccldevcomm)
              - [ncclDevCommCreate](api/device.html#nccldevcommcreate)
              - [ncclDevCommDestroy](api/device.html#nccldevcommdestroy)
              - [ncclDevCommRequirements](api/device.html#nccldevcommrequirements)
          - [LSA](api/device.html#lsa)
              - [ncclLsaBarrierSession](api/device.html#nccllsabarriersession)
              - [ncclGetPeerPointer](api/device.html#ncclgetpeerpointer)
              - [ncclGetLsaPointer](api/device.html#ncclgetlsapointer)
              - [ncclGetLocalPointer](api/device.html#ncclgetlocalpointer)
          - [Multimem](api/device.html#multimem)
              - [ncclGetLsaMultimemPointer](api/device.html#ncclgetlsamultimempointer)
          - [GIN](api/device.html#gin)
              - [ncclGin](api/device.html#ncclgin)
              - [Signals and Counters](api/device.html#signals-and-counters)
              - [ncclGinBarrierSession](api/device.html#ncclginbarriersession)
  - [Migrating from NCCL 1 to NCCL 2](nccl1.html)
      - [Initialization](nccl1.html#initialization)
      - [Communication](nccl1.html#communication)
      - [Counts](nccl1.html#counts)
      - [In-place usage for AllGather and ReduceScatter](nccl1.html#in-place-usage-for-allgather-and-reducescatter)
      - [AllGather arguments order](nccl1.html#allgather-arguments-order)
      - [Datatypes](nccl1.html#datatypes)
      - [Error codes](nccl1.html#error-codes)
  - [Examples](examples.html)
      - [Communicator Creation and Destruction Examples](examples.html#communicator-creation-and-destruction-examples)
          - [Example 1: Single Process, Single Thread, Multiple Devices](examples.html#example-1-single-process-single-thread-multiple-devices)
          - [Example 2: One Device per Process or Thread](examples.html#example-2-one-device-per-process-or-thread)
          - [Example 3: Multiple Devices per Thread](examples.html#example-3-multiple-devices-per-thread)
          - [Example 4: Multiple communicators per device](examples.html#example-4-multiple-communicators-per-device)
      - [Communication Examples](examples.html#communication-examples)
          - [Example 1: One Device per Process or Thread](examples.html#example-1-one-device-per-process-or-thread)
          - [Example 2: Multiple Devices per Thread](examples.html#example-2-multiple-devices-per-thread)
  - [NCCL and MPI](mpi.html)
      - [API](mpi.html#api)
          - [Using multiple devices per process](mpi.html#using-multiple-devices-per-process)
          - [ReduceScatter operation](mpi.html#reducescatter-operation)
          - [Send and Receive counts](mpi.html#send-and-receive-counts)
          - [Other collectives and point-to-point operations](mpi.html#other-collectives-and-point-to-point-operations)
          - [In-place operations](mpi.html#in-place-operations)
      - [Using NCCL within an MPI Program](mpi.html#using-nccl-within-an-mpi-program)
          - [MPI Progress](mpi.html#mpi-progress)
          - [Inter-GPU Communication with CUDA-aware MPI](mpi.html#inter-gpu-communication-with-cuda-aware-mpi)
  - [Environment Variables](#)
      - [System configuration](#system-configuration)
          - [NCCL\_SOCKET\_IFNAME](#nccl-socket-ifname)
              - [Values accepted](#values-accepted)
          - [NCCL\_SOCKET\_FAMILY](#nccl-socket-family)
              - [Values accepted](#id2)
          - [NCCL\_SOCKET\_RETRY\_CNT](#nccl-socket-retry-cnt)
              - [Values accepted](#id3)
          - [NCCL\_SOCKET\_RETRY\_SLEEP\_MSEC](#nccl-socket-retry-sleep-msec)
              - [Values accepted](#id4)
          - [NCCL\_SOCKET\_NTHREADS](#nccl-socket-nthreads)
              - [Values accepted](#id5)
          - [NCCL\_NSOCKS\_PERTHREAD](#nccl-nsocks-perthread)
              - [Values accepted](#id6)
          - [NCCL\_CROSS\_NIC](#nccl-cross-nic)
              - [Values accepted](#id7)
          - [NCCL\_IB\_HCA](#nccl-ib-hca)
              - [Values accepted](#id8)
          - [NCCL\_IB\_TIMEOUT](#nccl-ib-timeout)
              - [Values accepted](#id9)
          - [NCCL\_IB\_RETRY\_CNT](#nccl-ib-retry-cnt)
              - [Values accepted](#id10)
          - [NCCL\_IB\_GID\_INDEX](#nccl-ib-gid-index)
              - [Values accepted](#id11)
          - [NCCL\_IB\_ADDR\_FAMILY](#nccl-ib-addr-family)
              - [Values accepted](#id12)
          - [NCCL\_IB\_ADDR\_RANGE](#nccl-ib-addr-range)
              - [Values accepted](#id13)
          - [NCCL\_IB\_ROCE\_VERSION\_NUM](#nccl-ib-roce-version-num)
              - [Values accepted](#id14)
          - [NCCL\_IB\_SL](#nccl-ib-sl)
              - [Values accepted](#id15)
          - [NCCL\_IB\_TC](#nccl-ib-tc)
              - [Values accepted](#id16)
          - [NCCL\_IB\_FIFO\_TC](#nccl-ib-fifo-tc)
              - [Values accepted](#id17)
          - [NCCL\_IB\_RETURN\_ASYNC\_EVENTS](#nccl-ib-return-async-events)
              - [Values accepted](#id18)
          - [NCCL\_OOB\_NET\_ENABLE](#nccl-oob-net-enable)
              - [Values accepted](#id19)
          - [NCCL\_OOB\_NET\_IFNAME](#nccl-oob-net-ifname)
              - [Values accepted](#id20)
          - [NCCL\_UID\_STAGGER\_THRESHOLD](#nccl-uid-stagger-threshold)
              - [Values accepted](#id21)
          - [NCCL\_UID\_STAGGER\_RATE](#nccl-uid-stagger-rate)
              - [Values accepted](#id22)
          - [NCCL\_NET](#nccl-net)
              - [Values accepted](#id23)
          - [NCCL\_NET\_PLUGIN](#nccl-net-plugin)
              - [Values accepted](#id24)
          - [NCCL\_TUNER\_PLUGIN](#nccl-tuner-plugin)
              - [Values accepted](#id25)
          - [NCCL\_PROFILER\_PLUGIN](#nccl-profiler-plugin)
              - [Values accepted](#id26)
          - [NCCL\_ENV\_PLUGIN](#nccl-env-plugin)
              - [Values accepted](#id27)
          - [NCCL\_IGNORE\_CPU\_AFFINITY](#nccl-ignore-cpu-affinity)
              - [Values accepted](#id28)
          - [NCCL\_CONF\_FILE](#nccl-conf-file)
              - [Values accepted](#id29)
          - [NCCL\_DEBUG](#nccl-debug)
              - [Values accepted](#id31)
          - [NCCL\_DEBUG\_FILE](#nccl-debug-file)
              - [Values accepted](#id32)
          - [NCCL\_DEBUG\_SUBSYS](#nccl-debug-subsys)
              - [Values accepted](#id33)
          - [NCCL\_DEBUG\_TIMESTAMP\_FORMAT](#nccl-debug-timestamp-format)
              - [Value accepted](#value-accepted)
          - [NCCL\_DEBUG\_TIMESTAMP\_LEVELS](#nccl-debug-timestamp-levels)
              - [Value accepted](#id34)
          - [NCCL\_COLLNET\_ENABLE](#nccl-collnet-enable)
              - [Value accepted](#id35)
          - [NCCL\_COLLNET\_NODE\_THRESHOLD](#nccl-collnet-node-threshold)
              - [Value accepted](#id36)
          - [NCCL\_CTA\_POLICY](#nccl-cta-policy)
              - [Value accepted](#id37)
          - [NCCL\_NETDEVS\_POLICY](#nccl-netdevs-policy)
              - [Value accepted](#id38)
          - [NCCL\_TOPO\_FILE](#nccl-topo-file)
              - [Value accepted](#id39)
          - [NCCL\_TOPO\_DUMP\_FILE](#nccl-topo-dump-file)
              - [Value accepted](#id40)
          - [NCCL\_SET\_THREAD\_NAME](#nccl-set-thread-name)
              - [Value accepted](#id41)
      - [Debugging](#debugging)
          - [NCCL\_P2P\_DISABLE](#nccl-p2p-disable)
              - [Values accepted](#id42)
          - [NCCL\_P2P\_LEVEL](#nccl-p2p-level)
              - [Values accepted](#id43)
              - [Integer Values (Legacy)](#integer-values-legacy)
          - [NCCL\_P2P\_DIRECT\_DISABLE](#nccl-p2p-direct-disable)
              - [Values accepted](#id44)
          - [NCCL\_SHM\_DISABLE](#nccl-shm-disable)
              - [Values accepted](#id45)
          - [NCCL\_BUFFSIZE](#nccl-buffsize)
              - [Values accepted](#id46)
          - [NCCL\_NTHREADS](#nccl-nthreads)
              - [Values accepted](#id47)
          - [NCCL\_MAX\_NCHANNELS](#nccl-max-nchannels)
              - [Values accepted](#id48)
          - [NCCL\_MIN\_NCHANNELS](#nccl-min-nchannels)
              - [Values accepted](#id49)
          - [NCCL\_CHECKS\_DISABLE](#nccl-checks-disable)
              - [Values accepted](#id50)
          - [NCCL\_CHECK\_POINTERS](#nccl-check-pointers)
              - [Values accepted](#id51)
          - [NCCL\_LAUNCH\_MODE](#nccl-launch-mode)
              - [Values accepted](#id52)
          - [NCCL\_IB\_DISABLE](#nccl-ib-disable)
              - [Values accepted](#id53)
          - [NCCL\_IB\_AR\_THRESHOLD](#nccl-ib-ar-threshold)
              - [Values accepted](#id54)
          - [NCCL\_IB\_QPS\_PER\_CONNECTION](#nccl-ib-qps-per-connection)
              - [Values accepted](#id55)
          - [NCCL\_IB\_SPLIT\_DATA\_ON\_QPS](#nccl-ib-split-data-on-qps)
              - [Values accepted](#id56)
          - [NCCL\_IB\_CUDA\_SUPPORT](#nccl-ib-cuda-support)
              - [Values accepted](#id57)
          - [NCCL\_IB\_PCI\_RELAXED\_ORDERING](#nccl-ib-pci-relaxed-ordering)
              - [Values accepted](#id58)
          - [NCCL\_IB\_ADAPTIVE\_ROUTING](#nccl-ib-adaptive-routing)
              - [Values accepted](#id59)
          - [NCCL\_IB\_ECE\_ENABLE](#nccl-ib-ece-enable)
              - [Values accepted](#id60)
          - [NCCL\_MEM\_SYNC\_DOMAIN](#nccl-mem-sync-domain)
              - [Values accepted](#id61)
          - [NCCL\_CUMEM\_ENABLE](#nccl-cumem-enable)
              - [Values accepted](#id62)
          - [NCCL\_CUMEM\_HOST\_ENABLE](#nccl-cumem-host-enable)
              - [Values accepted](#id63)
          - [NCCL\_NET\_GDR\_LEVEL (formerly NCCL\_IB\_GDR\_LEVEL)](#nccl-net-gdr-level-formerly-nccl-ib-gdr-level)
              - [Values accepted](#id64)
              - [Integer Values (Legacy)](#id65)
          - [NCCL\_NET\_GDR\_C2C](#nccl-net-gdr-c2c)
              - [Values accepted](#id66)
          - [NCCL\_NET\_GDR\_READ](#nccl-net-gdr-read)
              - [Values accepted](#id67)
          - [NCCL\_NET\_SHARED\_BUFFERS](#nccl-net-shared-buffers)
              - [Value accepted](#id68)
          - [NCCL\_NET\_SHARED\_COMMS](#nccl-net-shared-comms)
              - [Value accepted](#id69)
          - [NCCL\_SINGLE\_RING\_THRESHOLD](#nccl-single-ring-threshold)
              - [Values accepted](#id70)
          - [NCCL\_LL\_THRESHOLD](#nccl-ll-threshold)
              - [Values accepted](#id71)
          - [NCCL\_TREE\_THRESHOLD](#nccl-tree-threshold)
              - [Values accepted](#id72)
          - [NCCL\_ALGO](#nccl-algo)
              - [Values accepted](#id73)
          - [NCCL\_PROTO](#nccl-proto)
              - [Values accepted](#id74)
          - [NCCL\_NVB\_DISABLE](#nccl-nvb-disable)
              - [Value accepted](#id75)
          - [NCCL\_PXN\_DISABLE](#nccl-pxn-disable)
              - [Value accepted](#id76)
          - [NCCL\_P2P\_PXN\_LEVEL](#nccl-p2p-pxn-level)
              - [Value accepted](#id77)
          - [NCCL\_PXN\_C2C](#nccl-pxn-c2c)
              - [Value accepted](#id78)
          - [NCCL\_RUNTIME\_CONNECT](#nccl-runtime-connect)
              - [Value accepted](#id79)
          - [NCCL\_GRAPH\_REGISTER](#nccl-graph-register)
              - [Value accepted](#id81)
          - [NCCL\_LOCAL\_REGISTER](#nccl-local-register)
              - [Value accepted](#id82)
          - [NCCL\_LEGACY\_CUDA\_REGISTER](#nccl-legacy-cuda-register)
              - [Value accepted](#id83)
          - [NCCL\_WIN\_ENABLE](#nccl-win-enable)
              - [Value accepted](#id84)
          - [NCCL\_SET\_STACK\_SIZE](#nccl-set-stack-size)
              - [Value accepted](#id85)
          - [NCCL\_GRAPH\_MIXING\_SUPPORT](#nccl-graph-mixing-support)
              - [Value accepted](#id87)
          - [NCCL\_DMABUF\_ENABLE](#nccl-dmabuf-enable)
              - [Value accepted](#id88)
          - [NCCL\_P2P\_NET\_CHUNKSIZE](#nccl-p2p-net-chunksize)
              - [Values accepted](#id89)
          - [NCCL\_P2P\_LL\_THRESHOLD](#nccl-p2p-ll-threshold)
              - [Values accepted](#id90)
          - [NCCL\_ALLOC\_P2P\_NET\_LL\_BUFFERS](#nccl-alloc-p2p-net-ll-buffers)
              - [Values accepted](#id91)
          - [NCCL\_COMM\_BLOCKING](#nccl-comm-blocking)
              - [Values accepted](#id92)
          - [NCCL\_CGA\_CLUSTER\_SIZE](#nccl-cga-cluster-size)
              - [Values accepted](#id93)
          - [NCCL\_MAX\_CTAS](#nccl-max-ctas)
              - [Values accepted](#id94)
          - [NCCL\_MIN\_CTAS](#nccl-min-ctas)
              - [Values accepted](#id95)
          - [NCCL\_NVLS\_ENABLE](#nccl-nvls-enable)
              - [Values accepted](#id96)
          - [NCCL\_IB\_MERGE\_NICS](#nccl-ib-merge-nics)
              - [Values accepted](#id97)
          - [NCCL\_MNNVL\_ENABLE](#nccl-mnnvl-enable)
              - [Values accepted](#id98)
          - [NCCL\_MNNVL\_UUID](#nccl-mnnvl-uuid)
              - [Values accepted](#id99)
          - [NCCL\_MNNVL\_CLIQUE\_ID](#nccl-mnnvl-clique-id)
              - [Values accepted](#id100)
          - [NCCL\_RAS\_ENABLE](#nccl-ras-enable)
              - [Values accepted](#id101)
          - [NCCL\_RAS\_ADDR](#nccl-ras-addr)
              - [Values accepted](#id102)
          - [NCCL\_RAS\_TIMEOUT\_FACTOR](#nccl-ras-timeout-factor)
              - [Values accepted](#id103)
          - [NCCL\_LAUNCH\_ORDER\_IMPLICIT](#nccl-launch-order-implicit)
              - [Values accepted](#id105)
          - [NCCL\_LAUNCH\_RACE\_FATAL](#nccl-launch-race-fatal)
              - [Values accepted](#id106)
  - [Troubleshooting](troubleshooting.html)
      - [Errors](troubleshooting.html#errors)
      - [RAS](troubleshooting.html#ras)
          - [RAS](troubleshooting/ras.html)
              - [Principle of Operation](troubleshooting/ras.html#principle-of-operation)
              - [RAS Queries](troubleshooting/ras.html#ras-queries)
              - [Sample Output](troubleshooting/ras.html#sample-output)
      - [GPU Direct](troubleshooting.html#gpu-direct)
          - [GPU-to-GPU communication](troubleshooting.html#gpu-to-gpu-communication)
          - [GPU-to-NIC communication](troubleshooting.html#gpu-to-nic-communication)
          - [PCI Access Control Services (ACS)](troubleshooting.html#pci-access-control-services-acs)
      - [Topology detection](troubleshooting.html#topology-detection)
      - [Memory issues](troubleshooting.html#memory-issues)
          - [Shared memory](troubleshooting.html#shared-memory)
          - [Stack size](troubleshooting.html#stack-size)
          - [Unified Memory (UVM)](troubleshooting.html#unified-memory-uvm)
      - [Networking issues](troubleshooting.html#networking-issues)
          - [IP Network Interfaces](troubleshooting.html#ip-network-interfaces)
          - [IP Ports](troubleshooting.html#ip-ports)
          - [InfiniBand](troubleshooting.html#infiniband)
          - [RDMA over Converged Ethernet (RoCE)](troubleshooting.html#rdma-over-converged-ethernet-roce)

</div>

</div>

<div class="section wy-nav-content-wrap" data-toggle="wy-nav-shift">

** [NCCL](index.html)

<div class="wy-nav-content">

<div class="rst-content">

<div role="navigation" aria-label="breadcrumbs navigation">

  - [Docs](index.html) »
  - Environment Variables
  - [View page source](_sources/env.rst.txt)

-----

</div>

<div class="document" role="main" itemscope="itemscope" itemtype="http://schema.org/Article">

<div itemprop="articleBody">

<div id="environment-variables" class="section">

# Environment Variables[¶](#environment-variables "Permalink to this headline")

NCCL has an extensive set of environment variables to tune for specific usage.

Environment variables can also be set statically in /etc/nccl.conf (for an administrator to set system-wide values) or in ${NCCL\_CONF\_FILE} (since 2.23; see below). For example, those files could contain :

<div class="code C highlight-c++ notranslate">

<div class="highlight">

    NCCL_DEBUG=WARN
    NCCL_SOCKET_IFNAME==ens1f0

</div>

</div>

There are two categories of environment variables. Some are needed to make NCCL follow system-specific configuration, and can be kept in scripts and system configuration. Other parameters listed in the “Debugging” section should not be used in production nor retained in scripts, or only as workaround, and removed as soon as the issue is resolved. Keeping them set may result in sub-optimal behavior, crashes, or hangs.

<div id="system-configuration" class="section">

## System configuration[¶](#system-configuration "Permalink to this headline")

<div id="nccl-socket-ifname" class="section">

<span id="id1"></span>

### NCCL\_SOCKET\_IFNAME[¶](#nccl-socket-ifname "Permalink to this headline")

The `NCCL_SOCKET_IFNAME` variable specifies which IP interfaces to use for communication.

<div id="values-accepted" class="section">

#### Values accepted[¶](#values-accepted "Permalink to this headline")

Define to a list of prefixes to filter interfaces to be used by NCCL.

Multiple prefixes can be provided, separated by the `,` symbol.

Using the `^` symbol, NCCL will exclude interfaces starting with any prefix in that list.

To match (or not) an exact interface name, begin the prefix string with the `=` character.

Examples:

`eth` : Use all interfaces starting with `eth`, e.g. `eth0`, `eth1`, …

`=eth0` : Use only interface `eth0`

`=eth0,eth1` : Use only interfaces `eth0` and `eth1`

`^docker` : Do not use any interface starting with `docker`

`^=docker0` : Do not use interface `docker0`.

Note: By default, the loopback interface (`lo`) and docker interfaces (`docker*`) would not be selected unless there are no other interfaces available. If you prefer to use `lo` or `docker*` over other interfaces, you would need to explicitly select them using `NCCL_SOCKET_IFNAME`. The default algorithm will also favor interfaces starting with `ib` over others. Setting `NCCL_SOCKET_IFNAME` will bypass the automatic interface selection algorithm and may use all interfaces matching the manual selection.

</div>

</div>

<div id="nccl-socket-family" class="section">

### NCCL\_SOCKET\_FAMILY[¶](#nccl-socket-family "Permalink to this headline")

The `NCCL_SOCKET_FAMILY` variable allows users to force NCCL to use only IPv4 or IPv6 interface.

<div id="id2" class="section">

#### Values accepted[¶](#id2 "Permalink to this headline")

Set to `AF_INET` to force the use of IPv4, or `AF_INET6` to force IPv6 usage.

</div>

</div>

<div id="nccl-socket-retry-cnt" class="section">

### NCCL\_SOCKET\_RETRY\_CNT[¶](#nccl-socket-retry-cnt "Permalink to this headline")

(since 2.24)

The `NCCL_SOCKET_RETRY_CNT` variable specifies the number of times NCCL retries to establish a socket connection after an `ETIMEDOUT`, `ECONNREFUSED`, or `EHOSTUNREACH` error.

<div id="id3" class="section">

#### Values accepted[¶](#id3 "Permalink to this headline")

The default value is 34, any positive value is valid.

</div>

</div>

<div id="nccl-socket-retry-sleep-msec" class="section">

### NCCL\_SOCKET\_RETRY\_SLEEP\_MSEC[¶](#nccl-socket-retry-sleep-msec "Permalink to this headline")

(since 2.24)

The `NCCL_SOCKET_RETRY_SLEEP_MSEC` variable specifies the number of milliseconds NCCL waits before retrying to establish a socket connection after the first `ETIMEDOUT`, `ECONNREFUSED`, or `EHOSTUNREACH` error. For subsequent errors, the waiting time scales linearly with the error count. The total time will therefore be (N+1) \* N/2 \* `NCCL_SOCKET_RETRY_SLEEP_MSEC`, where N is given by `NCCL_SOCKET_RETRY_CNT`. With the default values of `NCCL_SOCKET_RETRY_CNT` and `NCCL_SOCKET_RETRY_SLEEP_MSEC`, the total retry time will be approx. 60 seconds.

<div id="id4" class="section">

#### Values accepted[¶](#id4 "Permalink to this headline")

The default value is 100 milliseconds, any positive value is valid.

</div>

</div>

<div id="nccl-socket-nthreads" class="section">

### NCCL\_SOCKET\_NTHREADS[¶](#nccl-socket-nthreads "Permalink to this headline")

(since 2.4.8)

The `NCCL_SOCKET_NTHREADS` variable specifies the number of CPU helper threads used per network connection for socket transport. Increasing this value may increase the socket transport performance, at the cost of a higher CPU usage.

<div id="id5" class="section">

#### Values accepted[¶](#id5 "Permalink to this headline")

1 to 16. On AWS, the default value is 2; on Google Cloud instances with the gVNIC network interface, the default value is 4 (since 2.5.6); in other cases, the default value is 1.

For generic 100G networks, this value can be manually set to 4. However, the product of `NCCL_SOCKET_NTHREADS` and `NCCL_NSOCKS_PERTHREAD` cannot exceed 64. See also `NCCL_NSOCKS_PERTHREAD`.

</div>

</div>

<div id="nccl-nsocks-perthread" class="section">

### NCCL\_NSOCKS\_PERTHREAD[¶](#nccl-nsocks-perthread "Permalink to this headline")

(since 2.4.8)

The `NCCL_NSOCKS_PERTHREAD` variable specifies the number of sockets opened by each helper thread of the socket transport. In environments where per-socket speed is limited, setting this variable larger than 1 may improve the network performance.

<div id="id6" class="section">

#### Values accepted[¶](#id6 "Permalink to this headline")

On AWS, the default value is 8; in other cases, the default value is 1.

For generic 100G networks, this value can be manually set to 4. However, the product of `NCCL_SOCKET_NTHREADS` and `NCCL_NSOCKS_PERTHREAD` cannot exceed 64. See also `NCCL_SOCKET_NTHREADS`.

</div>

</div>

<div id="nccl-cross-nic" class="section">

<span id="env-nccl-cross-nic"></span>

### NCCL\_CROSS\_NIC[¶](#nccl-cross-nic "Permalink to this headline")

The `NCCL_CROSS_NIC` variable controls whether NCCL should allow rings/trees to use different NICs, causing inter-node communication to use different NICs on different nodes.

To maximize inter-node communication performance when using multiple NICs, NCCL tries to use the same NICs when communicating between nodes, to allow for a network design where each NIC on a node connects to a different network switch (network rail), and avoid any risk of traffic flow interference. The `NCCL_CROSS_NIC` setting is therefore dependent on the network topology, and in particular on whether the network fabric is rail-optimized or not.

This has no effect on systems with only one NIC.

<div id="id7" class="section">

#### Values accepted[¶](#id7 "Permalink to this headline")

0: Always use the same NIC for the same ring/tree, to avoid crossing network rails. Suited for networks with per NIC switches (rails), with a slow inter-rail connection. Note that if the communicator does not contain the same GPUs on each node, NCCL may still need to communicate across NICs.

1: Allow the use of different NICs for the same ring/tree. This is suited for networks where all NICs from a node are connected to the same switch, hence trying to communicate across the same NICs does not help avoiding flow collisions.

2: (Default) Try to use the same NIC for the same ring/tree, but still allow for the use of different NICs if it would result in a better performance.

</div>

</div>

<div id="nccl-ib-hca" class="section">

### NCCL\_IB\_HCA[¶](#nccl-ib-hca "Permalink to this headline")

The `NCCL_IB_HCA` variable specifies which Host Channel Adapter (RDMA) interfaces to use for communication.

<div id="id8" class="section">

#### Values accepted[¶](#id8 "Permalink to this headline")

Define to filter IB Verbs interfaces to be used by NCCL. The list is comma-separated; port numbers can be specified using the `:` symbol. An optional prefix `^` indicates the list is an exclude list. A second optional prefix `=` indicates that the tokens are exact names, otherwise by default NCCL would treat each token as a prefix.

Examples:

`mlx5` : Use all ports of all cards starting with `mlx5`

`=mlx5_0:1,mlx5_1:1` : Use ports 1 of cards `mlx5_0` and `mlx5_1`.

`^=mlx5_1,mlx5_4` : Do not use cards `mlx5_1` and `mlx5_4`.

Note: using `mlx5_1` without a preceding `=` will select `mlx5_1` as well as `mlx5_10` to `mlx5_19`, if they exist. It is therefore always recommended to add the `=` prefix to ensure an exact match.

Note: There is a fixed upper limit of 32 Host Channel Adapter (HCA) devices supported in NCCL.

</div>

</div>

<div id="nccl-ib-timeout" class="section">

### NCCL\_IB\_TIMEOUT[¶](#nccl-ib-timeout "Permalink to this headline")

The `NCCL_IB_TIMEOUT` variable controls the InfiniBand Verbs Timeout.

The timeout is computed as 4.096 µs \* 2 ^ *timeout*, and the correct value is dependent on the size of the network. Increasing that value can help on very large networks, for example, if NCCL is failing on a call to *ibv\_poll\_cq* with error 12.

For more information, see section 12.7.34 of the InfiniBand specification Volume 1 (Local Ack Timeout).

<div id="id9" class="section">

#### Values accepted[¶](#id9 "Permalink to this headline")

The default value used by NCCL is 20 (since 2.23; it was 18 since 2.14, and 14 before that).

Values can be 1-31.

Note: Setting a value of 0 or \>= 32 will result in an infinite timeout value.

</div>

</div>

<div id="nccl-ib-retry-cnt" class="section">

### NCCL\_IB\_RETRY\_CNT[¶](#nccl-ib-retry-cnt "Permalink to this headline")

(since 2.1.15)

The `NCCL_IB_RETRY_CNT` variable controls the InfiniBand retry count.

For more information, see section 12.7.38 of the InfiniBand specification Volume 1.

<div id="id10" class="section">

#### Values accepted[¶](#id10 "Permalink to this headline")

The default value is 7.

</div>

</div>

<div id="nccl-ib-gid-index" class="section">

### NCCL\_IB\_GID\_INDEX[¶](#nccl-ib-gid-index "Permalink to this headline")

(since 2.1.4)

The `NCCL_IB_GID_INDEX` variable defines the Global ID index used in RoCE mode. See the InfiniBand *show\_gids* command in order to set this value.

For more information, see the InfiniBand specification Volume 1 or vendor documentation.

<div id="id11" class="section">

#### Values accepted[¶](#id11 "Permalink to this headline")

The default value is -1.

</div>

</div>

<div id="nccl-ib-addr-family" class="section">

### NCCL\_IB\_ADDR\_FAMILY[¶](#nccl-ib-addr-family "Permalink to this headline")

(since 2.21)

The `NCCL_IB_ADDR_FAMILY` variable defines the IP address family associated to the infiniband GID dynamically selected by NCCL when `NCCL_IB_GID_INDEX` is left unset.

<div id="id12" class="section">

#### Values accepted[¶](#id12 "Permalink to this headline")

The default value is “AF\_INET”.

</div>

</div>

<div id="nccl-ib-addr-range" class="section">

### NCCL\_IB\_ADDR\_RANGE[¶](#nccl-ib-addr-range "Permalink to this headline")

(since 2.21)

The `NCCL_IB_ADDR_RANGE` variable defines the range of valid GIDs dynamically selected by NCCL when `NCCL_IB_GID_INDEX` is left unset.

<div id="id13" class="section">

#### Values accepted[¶](#id13 "Permalink to this headline")

By default, ignored if unset.

GID ranges can be defined using the Classless Inter-Domain Routing (CIDR) format for IPv4 and IPv6 families.

</div>

</div>

<div id="nccl-ib-roce-version-num" class="section">

### NCCL\_IB\_ROCE\_VERSION\_NUM[¶](#nccl-ib-roce-version-num "Permalink to this headline")

(since 2.21)

The `NCCL_IB_ROCE_VERSION_NUM` variable defines the RoCE version associated to the infiniband GID dynamically selected by NCCL when `NCCL_IB_GID_INDEX` is left unset.

<div id="id14" class="section">

#### Values accepted[¶](#id14 "Permalink to this headline")

The default value is 2.

</div>

</div>

<div id="nccl-ib-sl" class="section">

### NCCL\_IB\_SL[¶](#nccl-ib-sl "Permalink to this headline")

(since 2.1.4)

Defines the InfiniBand Service Level.

For more information, see the InfiniBand specification Volume 1 or vendor documentation.

<div id="id15" class="section">

#### Values accepted[¶](#id15 "Permalink to this headline")

The default value is 0.

</div>

</div>

<div id="nccl-ib-tc" class="section">

### NCCL\_IB\_TC[¶](#nccl-ib-tc "Permalink to this headline")

(since 2.1.15)

Defines the InfiniBand traffic class field.

For more information, see the InfiniBand specification Volume 1 or vendor documentation.

<div id="id16" class="section">

#### Values accepted[¶](#id16 "Permalink to this headline")

The default value is 0.

</div>

</div>

<div id="nccl-ib-fifo-tc" class="section">

### NCCL\_IB\_FIFO\_TC[¶](#nccl-ib-fifo-tc "Permalink to this headline")

(since 2.22.3)

Defines the InfiniBand traffic class for control messages. Control messages are short RDMA write operations which control credit return, contrary to other RDMA operations transmitting large segments of data. This setting allows to have those messages use a high priority, low-latency traffic class and avoid being delayed by the rest of the traffic.

<div id="id17" class="section">

#### Values accepted[¶](#id17 "Permalink to this headline")

The default value is the traffic class set by NCCL\_IB\_TC, which defaults to 0 if not set.

</div>

</div>

<div id="nccl-ib-return-async-events" class="section">

### NCCL\_IB\_RETURN\_ASYNC\_EVENTS[¶](#nccl-ib-return-async-events "Permalink to this headline")

(since 2.23)

IB events are reported to the user as warnings. If enabled, NCCL will also stop IB communications upon fatal IB asynchronous events.

<div id="id18" class="section">

#### Values accepted[¶](#id18 "Permalink to this headline")

The default value is 1, set to 0 to disable

</div>

</div>

<div id="nccl-oob-net-enable" class="section">

### NCCL\_OOB\_NET\_ENABLE[¶](#nccl-oob-net-enable "Permalink to this headline")

(since 2.23) The variable `NCCL_OOB_NET_ENABLE` enables the use of NCCL net for out-of-band communications. Enabling the usage of NCCL net will change the implementation of the allgather performed during the communicator initialization.

<div id="id19" class="section">

#### Values accepted[¶](#id19 "Permalink to this headline")

Set the variable to 0 to disable, and to 1 to enable.

</div>

</div>

<div id="nccl-oob-net-ifname" class="section">

### NCCL\_OOB\_NET\_IFNAME[¶](#nccl-oob-net-ifname "Permalink to this headline")

(since 2.23) If NCCL net is enabled for out-of-band communication (see `NCCL_OOB_NET_ENABLE`), the `NCCL_OOB_NET_IFNAME` variable specifies which network interfaces to use.

<div id="id20" class="section">

#### Values accepted[¶](#id20 "Permalink to this headline")

Define to filter interfaces to be used by NCCL for out-of-band communications. The list of accepted interface depends on the network used by NCCL. The list is comma-separated; port numbers can be specified using the `:` symbol. An optional prefix `^` indicates the list is an exclude list. A second optional prefix `=` indicates that the tokens are exact names, otherwise by default NCCL would treat each token as a prefix. If multiple devices are specified, NCCL will select the first matching device in the list.

Example:

`NCCL_NET="IB" NCCL_OOB_NET_ENABLE=1 NCCL_OOB_NET_IFNAME="=mlx5_1"` will use the Infiniband NET, with the interface `mlx5_1`

`NCCL_NET="IB" NCCL_OOB_NET_ENABLE=1 NCCL_OOB_NET_IFNAME="mlx5_1"` will use the Infiniband NET, with the first interface found in the list of `mlx5_1`, `mlx5_10`, `mlx5_11`, etc.

`NCCL_NET="Socket" NCCL_OOB_NET_ENABLE=1 NCCL_OOB_NET_IFNAME="ens1"` will use the socket NET, with the first interface found in the list of `ens1f0`, `ens1f1`, etc.

</div>

</div>

<div id="nccl-uid-stagger-threshold" class="section">

### NCCL\_UID\_STAGGER\_THRESHOLD[¶](#nccl-uid-stagger-threshold "Permalink to this headline")

(since 2.23) The `NCCL_UID_STAGGER_THRESHOLD` variable is used to trigger staggering of communications between NCCL ranks and the ncclUniqueId in order to avoid overflowing the ncclUniqueId. If the number of NCCL ranks communicating exceeds the specified threshold, the communications are staggered using the rank value (see NCCL\_UID\_STAGGER\_RATE below). If the number of NCCL ranks per ncclUniqueId is smaller or equal to the threshold, no staggering is performed.

For example, if we have 128 NCCL ranks, 1 ncclUniqueId, and a threshold at 64, staggering is performed. However, if 2 ncclUniqueIds are used with 128 NCCL ranks and a threshold at 64, no staggering is done.

<div id="id21" class="section">

#### Values accepted[¶](#id21 "Permalink to this headline")

The value of `NCCL_UID_STAGGER_THRESHOLD` must be a strictly positive integer. If unspecified, the default value is 256.

</div>

</div>

<div id="nccl-uid-stagger-rate" class="section">

### NCCL\_UID\_STAGGER\_RATE[¶](#nccl-uid-stagger-rate "Permalink to this headline")

(since 2.23)

The `NCCL_UID_STAGGER_RATE` variable is used to define the message rate targeted when staggering the communications between NCCL ranks and the ncclUniqueId. If staggering is used (see NCCL\_UID\_STAGGER\_THRESHOLD above), the message rate is used to compute the time a given NCCL rank has to wait.

<div id="id22" class="section">

#### Values accepted[¶](#id22 "Permalink to this headline")

The value of `NCCL_UID_STAGGER_RATE` must be a strictly positive integer, expressed in messages/second. If unspecified, the default value is 7000.

</div>

</div>

<div id="nccl-net" class="section">

### NCCL\_NET[¶](#nccl-net "Permalink to this headline")

(since 2.10)

Forces NCCL to use a specific network, for example to make sure NCCL uses an external plugin and doesn’t automatically fall back on the internal IB or Socket implementation. Setting this environment variable will override the `netName` configuration in all communicators (see [<span class="std std-ref">ncclConfig\_t</span>](api/types.html#ncclconfig)); if not set (undefined), the network module will be determined by the configuration; if not passing configuration, NCCL will automatically choose the best network module.

<div id="id23" class="section">

#### Values accepted[¶](#id23 "Permalink to this headline")

The value of NCCL\_NET has to match exactly the name of the NCCL network used (case-insensitive). Internal network names are “IB” (generic IB verbs) and “Socket” (TCP/IP sockets). External network plugins define their own names. Default value is undefined.

</div>

</div>

<div id="nccl-net-plugin" class="section">

### NCCL\_NET\_PLUGIN[¶](#nccl-net-plugin "Permalink to this headline")

(since 2.11)

  - Set it to either a suffix string or to a library name to choose among multiple NCCL net plugins. This setting will cause NCCL to look for the net plugin library using the following strategy:
    
      - If NCCL\_NET\_PLUGIN is set, attempt loading the library with name specified by NCCL\_NET\_PLUGIN;
      - If NCCL\_NET\_PLUGIN is set and previous failed, attempt loading libnccl-net-\<NCCL\_NET\_PLUGIN\>.so;
      - If NCCL\_NET\_PLUGIN is not set, attempt loading libnccl-net.so;
      - If no plugin was found (neither user defined nor default), use internal network plugin.

For example, setting `NCCL_NET_PLUGIN=foo` will cause NCCL to try load `foo` and, if `foo` cannot be found, `libnccl-net-foo.so` (provided that it exists on the system).

<div id="id24" class="section">

#### Values accepted[¶](#id24 "Permalink to this headline")

Plugin suffix, plugin file name, or “none”.

</div>

</div>

<div id="nccl-tuner-plugin" class="section">

### NCCL\_TUNER\_PLUGIN[¶](#nccl-tuner-plugin "Permalink to this headline")

  - Set it to either a suffix string or to a library name to choose among multiple NCCL tuner plugins. This setting will cause NCCL to look for the tuner plugin library using the following strategy:
    
      - If NCCL\_TUNER\_PLUGIN is set, attempt loading the library with name specified by NCCL\_TUNER\_PLUGIN;
      - If NCCL\_TUNER\_PLUGIN is set and previous failed, attempt loading libnccl-net-\<NCCL\_TUNER\_PLUGIN\>.so;
      - If NCCL\_TUNER\_PLUGIN is not set, attempt loading libnccl-tuner.so;
      - If no plugin was found look for the tuner symbols in the net plugin (refer to `NCCL_NET_PLUGIN`);
      - If no plugin was found (neither through NCCL\_TUNER\_PLUGIN nor NCCL\_NET\_PLUGIN), use internal tuner plugin.

For example, setting `NCCL_TUNER_PLUGIN=foo` will cause NCCL to try load `foo` and, if `foo` cannot be found, `libnccl-tuner-foo.so` (provided that it exists on the system).

<div id="id25" class="section">

#### Values accepted[¶](#id25 "Permalink to this headline")

Plugin suffix, plugin file name, or “none”.

</div>

</div>

<div id="nccl-profiler-plugin" class="section">

### NCCL\_PROFILER\_PLUGIN[¶](#nccl-profiler-plugin "Permalink to this headline")

  - Set it to either a suffix string or to a library name to choose among multiple NCCL profiler plugins. This setting will cause NCCL to look for the profiler plugin library using the following strategy:
    
      - If NCCL\_PROFILER\_PLUGIN is set, attempt loading the library with name specified by NCCL\_PROFILER\_PLUGIN;
      - If NCCL\_PROFILER\_PLUGIN is set and previous failed, attempt loading libnccl-profiler-\<NCCL\_PROFILER\_PLUGIN\>.so;
      - If NCCL\_PROFILER\_PLUGIN is not set, attempt loading libnccl-profiler.so;
      - If no plugin was found (neither user defined nor default), do not enable profiling.
      - If NCCL\_PROFILER\_PLUGIN is set to `STATIC_PLUGIN`, the plugin symbols are searched in the program binary.

For example, setting `NCCL_PROFILER_PLUGIN=foo` will cause NCCL to try load `foo` and, if `foo` cannot be found, `libnccl-profiler-foo.so` (provided that it exists on the system).

<div id="id26" class="section">

#### Values accepted[¶](#id26 "Permalink to this headline")

Plugin suffix, plugin file name, or “none”.

</div>

</div>

<div id="nccl-env-plugin" class="section">

### NCCL\_ENV\_PLUGIN[¶](#nccl-env-plugin "Permalink to this headline")

(since 2.28)

  - The `NCCL_ENV_PLUGIN` variable can be used to let NCCL load an external environment plugin. Set it to either a library name or a suffix string to choose among multiple NCCL environment plugins. This setting will cause NCCL to look for the environment plugin library using the following strategy:
    
      - If `NCCL_ENV_PLUGIN` is set to a library name, attempt loading that library (e.g. `NCCL_ENV_PLUGIN=/path/to/library/libfoo.so` will cause NCCL to try load `/path/to/library/libfoo.so`);
      - If `NCCL_ENV_PLUGIN` is set to a suffix string, attempt loading `libnccl-env-<NCCL_ENV_PLUGIN>.so` (e.g. `NCCL_ENV_PLUGIN=foo` will cause NCCL to try load `libnccl-env-foo.so` from the system library path);
      - If `NCCL_ENV_PLUGIN` is not set, attempt loading the default `libnccl-env.so` library from the system library path;
      - If `NCCL_ENV_PLUGIN` is set to “none”, explicitly disable the external plugin and use the internal one;
      - If no plugin was found (neither user defined nor default) or the variable is set to “none”, use the internal environment plugin.

<div id="id27" class="section">

#### Values accepted[¶](#id27 "Permalink to this headline")

Plugin library name (e.g., `/path/to/library/libfoo.so`), suffix (e.g., `foo`), or “none”.

</div>

</div>

<div id="nccl-ignore-cpu-affinity" class="section">

### NCCL\_IGNORE\_CPU\_AFFINITY[¶](#nccl-ignore-cpu-affinity "Permalink to this headline")

(since 2.4.6)

The `NCCL_IGNORE_CPU_AFFINITY` variable can be used to cause NCCL to ignore the job’s supplied CPU affinity and instead use the GPU affinity only.

<div id="id28" class="section">

#### Values accepted[¶](#id28 "Permalink to this headline")

The default is 0, set to 1 to cause NCCL to ignore the job’s supplied CPU affinity.

</div>

</div>

<div id="nccl-conf-file" class="section">

### NCCL\_CONF\_FILE[¶](#nccl-conf-file "Permalink to this headline")

(since 2.23)

The `NCCL_CONF_FILE` variable allows the user to specify a file with the static configuration. This does not accept the `~` character as part of the path; please convert to a relative or absolute path first.

<div id="id29" class="section">

#### Values accepted[¶](#id29 "Permalink to this headline")

If unset or if the version is prior to 2.23, NCCL uses .nccl.conf in the home directory if available.

</div>

</div>

<div id="nccl-debug" class="section">

<span id="id30"></span>

### NCCL\_DEBUG[¶](#nccl-debug "Permalink to this headline")

The `NCCL_DEBUG` variable controls the debug information that is displayed from NCCL. This variable is commonly used for debugging.

<div id="id31" class="section">

#### Values accepted[¶](#id31 "Permalink to this headline")

VERSION - Prints the NCCL version at the start of the program.

WARN - Prints an explicit error message whenever any NCCL call errors out.

INFO - Prints debug information

TRACE - Prints replayable trace information on every call.

</div>

</div>

<div id="nccl-debug-file" class="section">

### NCCL\_DEBUG\_FILE[¶](#nccl-debug-file "Permalink to this headline")

(since 2.2.12)

The `NCCL_DEBUG_FILE` variable directs the NCCL debug logging output to a file. The filename format can be set to *filename.%h.%p* where *%h* is replaced with the hostname and *%p* is replaced with the process PID. This does not accept the `~` character as part of the path, please convert to a relative or absolute path first.

<div id="id32" class="section">

#### Values accepted[¶](#id32 "Permalink to this headline")

The default output file is *stdout* unless this environment variable is set. The filename can also be set to `/dev/stdout` or `/dev/stderr` to direct NCCL debug logging output to those predefined I/O streams. This also has the effect of making the output line buffered.

Setting `NCCL_DEBUG_FILE` will cause NCCL to create and overwrite any previous files of that name.

Note: If the filename is not unique across all the job processes, then the output may be lost or corrupted.

</div>

</div>

<div id="nccl-debug-subsys" class="section">

### NCCL\_DEBUG\_SUBSYS[¶](#nccl-debug-subsys "Permalink to this headline")

(since 2.3.4)

The `NCCL_DEBUG_SUBSYS` variable allows the user to filter the `NCCL_DEBUG=INFO` output based on subsystems. The value should be a comma separated list of the subsystems to include in the NCCL debug log traces.

Prefixing the subsystem name with ‘^’ will disable the logging for that subsystem.

<div id="id33" class="section">

#### Values accepted[¶](#id33 "Permalink to this headline")

The default value is INIT,BOOTSTRAP,ENV.

Supported subsystem names are INIT (stands for initialization), COLL (stands for collectives), P2P (stands for peer-to-peer), SHM (stands for shared memory), NET (stands for network), GRAPH (stands for topology detection and graph search), TUNING (stands for algorithm/protocol tuning), ENV (stands for environment settings), ALLOC (stands for memory allocations), CALL (standard for function calls), PROXY (stands for the proxy thread operations), NVLS (standard for NVLink SHARP), BOOTSTRAP (stands for early initialization), REG (stands for memory registration), PROFILE (stands for coarse-grained profiling of initialization), RAS (stands for reliability, availability, and serviceability subsystem) and ALL (includes every subsystem).

</div>

</div>

<div id="nccl-debug-timestamp-format" class="section">

### NCCL\_DEBUG\_TIMESTAMP\_FORMAT[¶](#nccl-debug-timestamp-format "Permalink to this headline")

(since 2.26)

The `NCCL_DEBUG_TIMESTAMP_FORMAT` variable allows the user to change the format used when printing debug log messages.

The time is printed as a local time. This can be changed by setting the `TZ` environment variable. UTC is available by setting `TZ=UTC`. Valid values for TZ look like: `US/Pacific`, `America/Los_Angeles`, etc.

Note that the non-call `TRACE` level of logs continues to print the microseconds since the NCCL debug subsystem was initialized. The `TRACE` logs can also print the strftime formatted timestamp at the beginning if so configured (see `NCCL_DEBUG_TIMESTAMP_LEVELS`).

(since 2.26) Underscores in the format are rendered as spaces.

<div id="value-accepted" class="section">

#### Value accepted[¶](#value-accepted "Permalink to this headline")

The value of the environment variable is passed to strftime, so any valid format will work here. The default is ` [%F %T]  `, which is ` [YYYY-MM-DD HH:MM:SS]  `. If the value is set, but empty, then no timestamp will be printed (`NCCL_DEBUG_TIMESTAMP_FORMAT=`).

In addition to conversion specifications supported by strftime, `%Xf` can be specified, where `X` is a single numerical digit from 1-9. This will print fractions of a second. The value of `X` indicates how many digits will be printed. For example, `%3f` will print milliseconds. The value is zero padded. For example: ` [%F %T.%9f]  `. (Note that this can only be used once in the format string.)

</div>

</div>

<div id="nccl-debug-timestamp-levels" class="section">

### NCCL\_DEBUG\_TIMESTAMP\_LEVELS[¶](#nccl-debug-timestamp-levels "Permalink to this headline")

(since 2.26)

The `NCCL_DEBUG_TIMESTAMP_LEVELS` variable allows the user to set which log lines get a timestamp depending upon the level of the log.

<div id="id34" class="section">

#### Value accepted[¶](#id34 "Permalink to this headline")

The value should be a comma separated list of the levels which should have the timestamp. Valid levels are: `VERSION`, `WARN`, `INFO`, `ABORT`, and `TRACE`. In addition, `ALL` can be used to turn it on for all levels. Setting it to an empty value disables it for all levels. If the value is prefixed with a caret (`^`) then the listed levels will NOT log a timestamp, and the rest will. The default is to enable timestamps for `WARN`, but disable it for the rest.

For example, `NCCL_DEBUG_TIMESTAMP_LEVELS=WARN,INFO,TRACE` will turn it on for warnings, info logs, and traces. Or, `NCCL_DEBUG_TIMESTAMP_LEVELS=^TRACE` will turn them on for everything but traces, which (except call traces) have their own type of timestamp (microseconds since nccl debug initialization).

</div>

</div>

<div id="nccl-collnet-enable" class="section">

### NCCL\_COLLNET\_ENABLE[¶](#nccl-collnet-enable "Permalink to this headline")

(since 2.6)

Enable the use of the CollNet plugin.

<div id="id35" class="section">

#### Value accepted[¶](#id35 "Permalink to this headline")

Default is 0, define and set to 1 to use the CollNet plugin.

</div>

</div>

<div id="nccl-collnet-node-threshold" class="section">

### NCCL\_COLLNET\_NODE\_THRESHOLD[¶](#nccl-collnet-node-threshold "Permalink to this headline")

(since 2.9.9)

A threshold for the number of nodes below which CollNet will not be enabled.

<div id="id36" class="section">

#### Value accepted[¶](#id36 "Permalink to this headline")

Default is 2, define and set to an integer.

</div>

</div>

<div id="nccl-cta-policy" class="section">

### NCCL\_CTA\_POLICY[¶](#nccl-cta-policy "Permalink to this headline")

(since 2.27)

The `NCCL_CTA_POLICY` variable allows the user to set the policy for the NCCL communicator.

<div id="id37" class="section">

#### Value accepted[¶](#id37 "Permalink to this headline")

Set to 0 to use NCCL\_CTA\_POLICY\_DEFAULT policy (default); Set to 1 to use NCCL\_CTA\_POLICY\_EFFICIENCY policy. Set to 2 to use NCCL\_CTA\_POLICY\_ZERO policy. For more explanation about NCCL policies, please see [<span class="std std-ref">NCCL Communicator CTA Policy Flags</span>](api/flags.html#cta-policy-flags).

</div>

</div>

<div id="nccl-netdevs-policy" class="section">

### NCCL\_NETDEVS\_POLICY[¶](#nccl-netdevs-policy "Permalink to this headline")

(since 2.28)

The `NCCL_NETDEVS_POLICY` variable allows the user to set the policy for the assignment of network devices to the GPUs. For each GPU, NCCL detects automatically available network devices, taking into account their network bandwidth and the node topology.

<div id="id38" class="section">

#### Value accepted[¶](#id38 "Permalink to this headline")

If set to `AUTO` (default), NCCL also takes into account the other GPUs in the same communicator in order to assign network devices. In specific scenarios, this policy might lead to different GPUs from different communicators sharing the same network devices, and therefore impacts performance.

If set to `MAX:N`, NCCL uses up to N of the network devices available to each GPU. This is intended to be used when device sharing happens with `AUTO` and impacts the performance.

If set to `ALL`, NCCL will use all the available network devices for each GPU, disregarding other GPUs.

</div>

</div>

<div id="nccl-topo-file" class="section">

### NCCL\_TOPO\_FILE[¶](#nccl-topo-file "Permalink to this headline")

(since 2.6)

Path to an XML file to load before detecting the topology. By default, NCCL will load `/var/run/nvidia-topologyd/virtualTopology.xml` if present.

<div id="id39" class="section">

#### Value accepted[¶](#id39 "Permalink to this headline")

A path to an accessible file describing part or all of the topology.

</div>

</div>

<div id="nccl-topo-dump-file" class="section">

### NCCL\_TOPO\_DUMP\_FILE[¶](#nccl-topo-dump-file "Permalink to this headline")

(since 2.6)

Path to a file to dump the XML topology to after detection.

<div id="id40" class="section">

#### Value accepted[¶](#id40 "Permalink to this headline")

A path to a file which will be created or overwritten.

</div>

</div>

<div id="nccl-set-thread-name" class="section">

### NCCL\_SET\_THREAD\_NAME[¶](#nccl-set-thread-name "Permalink to this headline")

(since 2.12)

Give more meaningful names to NCCL CPU threads to ease debugging and analysis.

<div id="id41" class="section">

#### Value accepted[¶](#id41 "Permalink to this headline")

0 or 1. Default is 0 (disabled).

</div>

</div>

</div>

<div id="debugging" class="section">

## Debugging[¶](#debugging "Permalink to this headline")

These environment variables should be used with caution. New versions of NCCL could work differently and forcing them to a particular value will prevent NCCL from selecting the best setting automatically. They can therefore cause performance problems in the long term, or even break some functionality.

They are fine to use for experiments, or to debug a problem, but should generally not be set for production code.

<div id="nccl-p2p-disable" class="section">

### NCCL\_P2P\_DISABLE[¶](#nccl-p2p-disable "Permalink to this headline")

The `NCCL_P2P_DISABLE` variable disables the peer to peer (P2P) transport, which uses CUDA direct access between GPUs, using NVLink or PCI.

<div id="id42" class="section">

#### Values accepted[¶](#id42 "Permalink to this headline")

Define and set to 1 to disable direct GPU-to-GPU (P2P) communication.

</div>

</div>

<div id="nccl-p2p-level" class="section">

<span id="env-nccl-p2p-level"></span>

### NCCL\_P2P\_LEVEL[¶](#nccl-p2p-level "Permalink to this headline")

(since 2.3.4)

The `NCCL_P2P_LEVEL` variable allows the user to finely control when to use the peer to peer (P2P) transport between GPUs. The level defines the maximum distance between GPUs where NCCL will use the P2P transport. A short string representing the path type should be used to specify the topographical cutoff for using the P2P transport.

If this isn’t specified, NCCL will attempt to optimally select a value based on the architecture and environment it’s run in.

<div id="id43" class="section">

#### Values accepted[¶](#id43 "Permalink to this headline")

  - LOC : Never use P2P (always disabled)
  - NVL : Use P2P when GPUs are connected through NVLink
  - PIX : Use P2P when GPUs are on the same PCI switch.
  - PXB : Use P2P when GPUs are connected through PCI switches (potentially multiple hops).
  - PHB : Use P2P when GPUs are on the same NUMA node. Traffic will go through the CPU.
  - SYS : Use P2P between NUMA nodes, potentially crossing the SMP interconnect (e.g. QPI/UPI).

</div>

<div id="integer-values-legacy" class="section">

#### Integer Values (Legacy)[¶](#integer-values-legacy "Permalink to this headline")

There is also the option to declare `NCCL_P2P_LEVEL` as an integer corresponding to the path type. These numerical values were kept for retro-compatibility, for those who used numerical values before strings were allowed.

Integer values are discouraged due to breaking changes in path types - the literal values can change over time. To avoid headaches debugging your configuration, use string identifiers.

  - LOC : 0
  - PIX : 1
  - PXB : 2
  - PHB : 3
  - SYS : 4

Values greater than 4 will be interpreted as SYS. NVL is not supported using the legacy integer values.

</div>

</div>

<div id="nccl-p2p-direct-disable" class="section">

### NCCL\_P2P\_DIRECT\_DISABLE[¶](#nccl-p2p-direct-disable "Permalink to this headline")

The `NCCL_P2P_DIRECT_DISABLE` variable forbids NCCL to directly access user buffers through P2P between GPUs of the same process. This is useful when user buffers are allocated with APIs which do not automatically make them accessible to other GPUs managed by the same process and with P2P access.

<div id="id44" class="section">

#### Values accepted[¶](#id44 "Permalink to this headline")

Define and set to 1 to disable direct user buffer access across GPUs.

</div>

</div>

<div id="nccl-shm-disable" class="section">

### NCCL\_SHM\_DISABLE[¶](#nccl-shm-disable "Permalink to this headline")

The `NCCL_SHM_DISABLE` variable disables the Shared Memory (SHM) transports. SHM is used between devices when peer-to-peer cannot happen, therefore, host memory is used. NCCL will use the network (i.e. InfiniBand or IP sockets) to communicate between the CPU sockets when SHM is disabled.

<div id="id45" class="section">

#### Values accepted[¶](#id45 "Permalink to this headline")

Define and set to 1 to disable communication through shared memory (SHM).

</div>

</div>

<div id="nccl-buffsize" class="section">

### NCCL\_BUFFSIZE[¶](#nccl-buffsize "Permalink to this headline")

The `NCCL_BUFFSIZE` variable controls the size of the buffer used by NCCL when communicating data between pairs of GPUs.

Use this variable if you encounter memory constraint issues when using NCCL or you think that a different buffer size would improve performance.

<div id="id46" class="section">

#### Values accepted[¶](#id46 "Permalink to this headline")

The default is 4194304 (4 MiB).

Values are integers, in bytes. The recommendation is to use powers of 2. For example, 1024 will give a 1KiB buffer.

</div>

</div>

<div id="nccl-nthreads" class="section">

### NCCL\_NTHREADS[¶](#nccl-nthreads "Permalink to this headline")

The `NCCL_NTHREADS` variable sets the number of CUDA threads per CUDA block. NCCL will launch one CUDA block per communication channel.

Use this variable if you think your GPU clocks are low and you want to increase the number of threads.

You can also use this variable to reduce the number of threads to decrease the GPU workload.

<div id="id47" class="section">

#### Values accepted[¶](#id47 "Permalink to this headline")

The default is 512 for recent generation GPUs, and 256 for some older generations.

The values allowed are 64, 128, 256 and 512.

</div>

</div>

<div id="nccl-max-nchannels" class="section">

### NCCL\_MAX\_NCHANNELS[¶](#nccl-max-nchannels "Permalink to this headline")

(NCCL\_MAX\_NRINGS since 2.0.5, NCCL\_MAX\_NCHANNELS since 2.5.0)

The `NCCL_MAX_NCHANNELS` variable limits the number of channels NCCL can use. Reducing the number of channels also reduces the number of CUDA blocks used for communication, hence the impact on GPU computing resources.

The old `NCCL_MAX_NRINGS` variable (used until 2.4) still works as an alias in newer versions but is ignored if `NCCL_MAX_NCHANNELS` is set.

This environment variable has been superseded by `NCCL_MAX_CTAS` which can also be set programmatically using [<span class="std std-ref">ncclCommInitRankConfig</span>](api/comms.html#ncclcomminitrankconfig).

<div id="id48" class="section">

#### Values accepted[¶](#id48 "Permalink to this headline")

Any value above or equal to 1.

</div>

</div>

<div id="nccl-min-nchannels" class="section">

### NCCL\_MIN\_NCHANNELS[¶](#nccl-min-nchannels "Permalink to this headline")

(NCCL\_MIN\_NRINGS since 2.2.0, NCCL\_MIN\_NCHANNELS since 2.5.0)

The `NCCL_MIN_NCHANNELS` variable controls the minimum number of channels you want NCCL to use. Increasing the number of channels also increases the number of CUDA blocks NCCL uses, which may be useful to improve performance; however, it uses more CUDA compute resources.

This is especially useful when using aggregated collectives on platforms where NCCL would usually only create one channel.

The old `NCCL_MIN_NRINGS` variable (used until 2.4) still works as an alias in newer versions, but is ignored if `NCCL_MIN_NCHANNELS` is set.

This environment variable has been superseded by `NCCL_MIN_CTAS` which can also be set programmatically using [<span class="std std-ref">ncclCommInitRankConfig</span>](api/comms.html#ncclcomminitrankconfig).

<div id="id49" class="section">

#### Values accepted[¶](#id49 "Permalink to this headline")

The default is platform dependent. Set to an integer value, up to 12 (up to 2.2), 16 (2.3 and 2.4) or 32 (2.5 and later).

</div>

</div>

<div id="nccl-checks-disable" class="section">

### NCCL\_CHECKS\_DISABLE[¶](#nccl-checks-disable "Permalink to this headline")

(since 2.0.5, deprecated in 2.2.12)

The `NCCL_CHECKS_DISABLE` variable can be used to disable argument checks on each collective call. Checks are useful during development but can increase the latency. They can be disabled to improve performance in production.

<div id="id50" class="section">

#### Values accepted[¶](#id50 "Permalink to this headline")

The default is 0, set to 1 to disable checks.

</div>

</div>

<div id="nccl-check-pointers" class="section">

### NCCL\_CHECK\_POINTERS[¶](#nccl-check-pointers "Permalink to this headline")

(since 2.2.12)

The `NCCL_CHECK_POINTERS` variable enables checking of the CUDA memory pointers on each collective call. Checks are useful during development but can increase the latency.

<div id="id51" class="section">

#### Values accepted[¶](#id51 "Permalink to this headline")

The default is 0, set to 1 to enable checking.

Setting to 1 restores the original behavior of NCCL prior to 2.2.12.

</div>

</div>

<div id="nccl-launch-mode" class="section">

### NCCL\_LAUNCH\_MODE[¶](#nccl-launch-mode "Permalink to this headline")

(since 2.1.0)

The `NCCL_LAUNCH_MODE` variable controls how NCCL launches CUDA kernels.

<div id="id52" class="section">

#### Values accepted[¶](#id52 "Permalink to this headline")

The default value is PARALLEL.

Setting is to GROUP will use cooperative groups (CUDA 9.0 and later) for processes managing more than one GPU. This is deprecated in 2.9 and may be removed in future versions.

</div>

</div>

<div id="nccl-ib-disable" class="section">

### NCCL\_IB\_DISABLE[¶](#nccl-ib-disable "Permalink to this headline")

The `NCCL_IB_DISABLE` variable prevents the IB/RoCE transport from being used by NCCL. Instead, NCCL will fall back to using IP sockets.

<div id="id53" class="section">

#### Values accepted[¶](#id53 "Permalink to this headline")

Define and set to 1 to disable the use of InfiniBand Verbs for communication (and force another method, e.g. IP sockets).

</div>

</div>

<div id="nccl-ib-ar-threshold" class="section">

### NCCL\_IB\_AR\_THRESHOLD[¶](#nccl-ib-ar-threshold "Permalink to this headline")

(since 2.6)

Threshold above which we send InfiniBand data in a separate message which can leverage adaptive routing.

<div id="id54" class="section">

#### Values accepted[¶](#id54 "Permalink to this headline")

Size in bytes, the default value is 8192.

Setting it above NCCL\_BUFFSIZE will disable the use of adaptive routing completely.

</div>

</div>

<div id="nccl-ib-qps-per-connection" class="section">

### NCCL\_IB\_QPS\_PER\_CONNECTION[¶](#nccl-ib-qps-per-connection "Permalink to this headline")

(since 2.10)

Number of IB queue pairs to use for each connection between two ranks. This can be useful on multi-level fabrics which need multiple queue pairs to have good routing entropy. See `NCCL_IB_SPLIT_DATA_ON_QPS` for different ways to split data on multiple QPs, as it can affect performance.

<div id="id55" class="section">

#### Values accepted[¶](#id55 "Permalink to this headline")

Number between 1 and 128, default is 1.

</div>

</div>

<div id="nccl-ib-split-data-on-qps" class="section">

### NCCL\_IB\_SPLIT\_DATA\_ON\_QPS[¶](#nccl-ib-split-data-on-qps "Permalink to this headline")

(since 2.18)

This parameter controls how we use the queue pairs when we create more than one. Set to 1 (split mode), each message will be split evenly on each queue pair. This may cause a visible latency degradation if many QPs are used. Set to 0 (round-robin mode), queue pairs will be used in round-robin mode for each message we send. Operations which do not send multiple messages will not use all QPs.

<div id="id56" class="section">

#### Values accepted[¶](#id56 "Permalink to this headline")

0 or 1. Default is 0 (since NCCL 2.20). Setting it to 1 will enable split mode (default in 2.18 and 2.19).

</div>

</div>

<div id="nccl-ib-cuda-support" class="section">

### NCCL\_IB\_CUDA\_SUPPORT[¶](#nccl-ib-cuda-support "Permalink to this headline")

(removed in 2.4.0, see NCCL\_NET\_GDR\_LEVEL)

The `NCCL_IB_CUDA_SUPPORT` variable is used to force or disable the usage of GPU Direct RDMA. By default, NCCL enables GPU Direct RDMA if the topology permits it. This variable can disable this behavior or force the usage of GPU Direct RDMA in all cases.

<div id="id57" class="section">

#### Values accepted[¶](#id57 "Permalink to this headline")

Define and set to 0 to disable GPU Direct RDMA.

Define and set to 1 to force the usage of GPU Direct RDMA.

</div>

</div>

<div id="nccl-ib-pci-relaxed-ordering" class="section">

### NCCL\_IB\_PCI\_RELAXED\_ORDERING[¶](#nccl-ib-pci-relaxed-ordering "Permalink to this headline")

(since 2.12)

Enable the use of Relaxed Ordering for the IB Verbs transport. Relaxed Ordering can greatly help the performance of InfiniBand networks in virtualized environments.

<div id="id58" class="section">

#### Values accepted[¶](#id58 "Permalink to this headline")

Set to 2 to automatically use Relaxed Ordering if available. Set to 1 to force the use of Relaxed Ordering and fail if not available. Set to 0 to disable the use of Relaxed Ordering. Default is 2.

</div>

</div>

<div id="nccl-ib-adaptive-routing" class="section">

### NCCL\_IB\_ADAPTIVE\_ROUTING[¶](#nccl-ib-adaptive-routing "Permalink to this headline")

(since 2.16)

Enable the use of Adaptive Routing capable data transfers for the IB Verbs transport. Adaptive routing can improve the performance of communications at scale. A system defined Adaptive Routing enabled SL has to be selected accordingly (cf. `NCCL_IB_SL`).

<div id="id59" class="section">

#### Values accepted[¶](#id59 "Permalink to this headline")

Enabled (1) by default on IB networks. Disabled (0) by default on RoCE networks. Set to 1 to force use of Adaptive Routing capable data transmission.

</div>

</div>

<div id="nccl-ib-ece-enable" class="section">

### NCCL\_IB\_ECE\_ENABLE[¶](#nccl-ib-ece-enable "Permalink to this headline")

(since 2.23)

Enable the use of Enhanced Connection Establishment (ECE) on IB/RoCE Verbs networks. ECE can be used to enable advanced networking features such as Congestion Control, Adaptive Routing and Selective Repeat. Note: These parameters are not interpreted or controlled by NCCL and are passed through directly to the HCAs via the ECE mechanism.

<div id="id60" class="section">

#### Values accepted[¶](#id60 "Permalink to this headline")

Enabled (1) by default (since 2.19). Set to 0 to disable use of ECE network capabilities.

Note: Incorrect configuration of the ECE parameters on a system can adversely affect NCCL performance. Administrators should ensure ECE is correctly configured if it is enabled at the system level.

</div>

</div>

<div id="nccl-mem-sync-domain" class="section">

### NCCL\_MEM\_SYNC\_DOMAIN[¶](#nccl-mem-sync-domain "Permalink to this headline")

(since 2.16)

Sets the default Memory Sync Domain for NCCL kernels (CUDA 12.0 & sm90 and later). Memory Sync Domains can help eliminate interference between the NCCL kernels and the application compute kernels, when they use different domains.

<div id="id61" class="section">

#### Values accepted[¶](#id61 "Permalink to this headline")

Default value is `cudaLaunchMemSyncDomainRemote` (1). Currently supported values are 0 and 1.

</div>

</div>

<div id="nccl-cumem-enable" class="section">

<span id="env-nccl-cumem-enable"></span>

### NCCL\_CUMEM\_ENABLE[¶](#nccl-cumem-enable "Permalink to this headline")

(since 2.18)

Use CUDA cuMem\* functions to allocate memory in NCCL.

<div id="id62" class="section">

#### Values accepted[¶](#id62 "Permalink to this headline")

0 or 1. Default is 0 in 2.18 (disabled); since 2.19 this feature is auto-enabled by default if the system supports it (NCCL\_CUMEM\_ENABLE can still be used to override the autodetection).

</div>

</div>

<div id="nccl-cumem-host-enable" class="section">

### NCCL\_CUMEM\_HOST\_ENABLE[¶](#nccl-cumem-host-enable "Permalink to this headline")

(since 2.23)

Use CUDA cuMem\* functions to allocate host memory in NCCL. See [<span class="std std-ref">Shared memory</span>](troubleshooting.html#cumem-host-allocations) for more information.

<div id="id63" class="section">

#### Values accepted[¶](#id63 "Permalink to this headline")

0 or 1. Default is 0 in 2.23; since 2.24, default is 1 if CUDA driver \>= 12.6, CUDA runtime \>= 12.2, and cuMem host allocations are supported.

</div>

</div>

<div id="nccl-net-gdr-level-formerly-nccl-ib-gdr-level" class="section">

### NCCL\_NET\_GDR\_LEVEL (formerly NCCL\_IB\_GDR\_LEVEL)[¶](#nccl-net-gdr-level-formerly-nccl-ib-gdr-level "Permalink to this headline")

(since 2.3.4. In 2.4.0, NCCL\_IB\_GDR\_LEVEL was renamed to NCCL\_NET\_GDR\_LEVEL)

The `NCCL_NET_GDR_LEVEL` variable allows the user to finely control when to use GPU Direct RDMA between a NIC and a GPU. The level defines the maximum distance between the NIC and the GPU. A string representing the path type should be used to specify the topographical cutoff for GpuDirect.

If this isn’t specified, NCCL will attempt to optimally select a value based on the architecture and environment it’s run in.

<div id="id64" class="section">

#### Values accepted[¶](#id64 "Permalink to this headline")

  - LOC : Never use GPU Direct RDMA (always disabled).
  - PIX : Use GPU Direct RDMA when GPU and NIC are on the same PCI switch.
  - PXB : Use GPU Direct RDMA when GPU and NIC are connected through PCI switches (potentially multiple hops).
  - PHB : Use GPU Direct RDMA when GPU and NIC are on the same NUMA node. Traffic will go through the CPU.
  - SYS : Use GPU Direct RDMA even across the SMP interconnect between NUMA nodes (e.g., QPI/UPI) (always enabled).

</div>

<div id="id65" class="section">

#### Integer Values (Legacy)[¶](#id65 "Permalink to this headline")

There is also the option to declare `NCCL_NET_GDR_LEVEL` as an integer corresponding to the path type. These numerical values were kept for retro-compatibility, for those who used numerical values before strings were allowed.

Integer values are discouraged due to breaking changes in path types - the literal values can change over time. To avoid headaches debugging your configuration, use string identifiers.

  - LOC : 0
  - PIX : 1
  - PXB : 2
  - PHB : 3
  - SYS : 4

Values greater than 4 will be interpreted as SYS.

</div>

</div>

<div id="nccl-net-gdr-c2c" class="section">

### NCCL\_NET\_GDR\_C2C[¶](#nccl-net-gdr-c2c "Permalink to this headline")

(since 2.26)

The `NCCL_NET_GDR_C2C` variable enables GPU Direct RDMA when sending data via a NIC attached to a CPU (i.e. distance PHB) where the CPU is connected to the GPU via a C2C interconnect. This effectively overrides the `NCCL_NET_GDR_LEVEL` setting for this particular NIC.

<div id="id66" class="section">

#### Values accepted[¶](#id66 "Permalink to this headline")

0 or 1. Define and set to 1 to use GPU Direct RDMA to send data to the NIC directly via C2C connected CPUs.

The default value was 0 in 2.26. The default value is 1 since 2.27.

</div>

</div>

<div id="nccl-net-gdr-read" class="section">

### NCCL\_NET\_GDR\_READ[¶](#nccl-net-gdr-read "Permalink to this headline")

The `NCCL_NET_GDR_READ` variable enables GPU Direct RDMA when sending data as long as the GPU-NIC distance is within the distance specified by `NCCL_NET_GDR_LEVEL`. Before 2.4.2, GDR read is disabled by default, i.e. when sending data, the data is first stored in CPU memory, then goes to the InfiniBand card. Since 2.4.2, GDR read is enabled by default for NVLink-based platforms.

Note: Reading directly from GPU memory when sending data is known to be slightly slower than reading from CPU memory on some platforms, such as PCI-E.

<div id="id67" class="section">

#### Values accepted[¶](#id67 "Permalink to this headline")

0 or 1. Define and set to 1 to use GPU Direct RDMA to send data to the NIC directly (bypassing CPU).

Before 2.4.2, the default value is 0 for all platforms. Since 2.4.2, the default value is 1 for NVLink-based platforms and 0 otherwise.

</div>

</div>

<div id="nccl-net-shared-buffers" class="section">

### NCCL\_NET\_SHARED\_BUFFERS[¶](#nccl-net-shared-buffers "Permalink to this headline")

(since 2.8)

Allows the usage of shared buffers for inter-node point-to-point communication. This will use a single large pool for all remote peers, having a constant memory usage instead of increasing linearly with the number of remote peers.

<div id="id68" class="section">

#### Value accepted[¶](#id68 "Permalink to this headline")

Default is 1 (enabled). Set to 0 to disable.

</div>

</div>

<div id="nccl-net-shared-comms" class="section">

### NCCL\_NET\_SHARED\_COMMS[¶](#nccl-net-shared-comms "Permalink to this headline")

(since 2.12)

Reuse the same connections in the context of PXN. This allows for message aggregation but can also decrease the entropy of network packets.

<div id="id69" class="section">

#### Value accepted[¶](#id69 "Permalink to this headline")

Default is 1 (enabled). Set to 0 to disable.

</div>

</div>

<div id="nccl-single-ring-threshold" class="section">

### NCCL\_SINGLE\_RING\_THRESHOLD[¶](#nccl-single-ring-threshold "Permalink to this headline")

(since 2.1, removed in 2.3)

The `NCCL_SINGLE_RING_THRESHOLD` variable sets the limit under which NCCL will only use one ring. This will limit bandwidth but improve latency.

<div id="id70" class="section">

#### Values accepted[¶](#id70 "Permalink to this headline")

The default value is 262144 (256kB) on GPUs with compute capability 7 and above. Otherwise, the default value is 131072 (128kB).

Values are integers, in bytes.

</div>

</div>

<div id="nccl-ll-threshold" class="section">

### NCCL\_LL\_THRESHOLD[¶](#nccl-ll-threshold "Permalink to this headline")

(since 2.1, removed in 2.5)

The `NCCL_LL_THRESHOLD` variable sets the size limit under which NCCL uses low-latency algorithms.

<div id="id71" class="section">

#### Values accepted[¶](#id71 "Permalink to this headline")

The default is 16384 (up to 2.2) or is dependent on the number of ranks (2.3 and later).

Values are integers, in bytes.

</div>

</div>

<div id="nccl-tree-threshold" class="section">

### NCCL\_TREE\_THRESHOLD[¶](#nccl-tree-threshold "Permalink to this headline")

(since 2.4, removed in 2.5)

The `NCCL_TREE_THRESHOLD` variable sets the size limit under which NCCL uses tree algorithms instead of rings.

<div id="id72" class="section">

#### Values accepted[¶](#id72 "Permalink to this headline")

The default is dependent on the number of ranks.

Values are integers, in bytes.

</div>

</div>

<div id="nccl-algo" class="section">

### NCCL\_ALGO[¶](#nccl-algo "Permalink to this headline")

(since 2.5)

The `NCCL_ALGO` variable defines which algorithms NCCL will use.

<div id="id73" class="section">

#### Values accepted[¶](#id73 "Permalink to this headline")

(since 2.5)

Comma-separated list of algorithms (not case sensitive) among:

| Version     | Algorithm     |
| ----------- | ------------- |
| 2.5+        | Ring          |
| 2.5+        | Tree          |
| 2.5 to 2.13 | Collnet       |
| 2.14+       | CollnetChain  |
| 2.14+       | CollnetDirect |
| 2.17+       | NVLS          |
| 2.18+       | NVLSTree      |
| 2.23+       | PAT           |

NVLS and NVLSTree enable NVLink SHARP offload.

To specify algorithms to exclude (instead of include), start the list with `^`.

(since 2.24)

The accepted values are expanded to allow more flexibility, and parsing will issue a warning and fail if an unexpected token is found. Also, if `ring` is not specified as a valid algorithm then it will not implicitly fall back to `ring` if there is no other valid algorithm for the function. Instead, it will fail.

The format is now a semicolon-separated list of pairs of function name and list of algorithms, where the function name is optional for the first entry. If not present, then it applies to all functions not later listed. A colon separates the function (when present) and the comma-separated list of algorithms. Also, if the first character of the comma-separated list of algorithms is a caret (`^`), then all the selections are inverted.

For example, `NCCL_ALGO="ring,collnetdirect;allreduce:tree,collnetdirect;broadcast:ring"` Will enable ring and collnetdirect for all functions, then enable tree and collnetdirect for allreduce and ring for broadcast.

And, `NCCL_ALGO=allreduce:^tree` will allow the default (all algorithms available) for all the functions except allreduce, which will have all algorithms available except tree.

The default is unset, which causes NCCL to automatically choose the available algorithms based on the node topology and architecture.

</div>

</div>

<div id="nccl-proto" class="section">

### NCCL\_PROTO[¶](#nccl-proto "Permalink to this headline")

(since 2.5)

The `NCCL_PROTO` variable defines which protocol(s) NCCL will be allowed to use.

Users are discouraged from setting this variable, with the exception of disabling a specific protocol in case a bug in NCCL is suspected. In particular, enabling LL128 on platforms that don’t support it can lead to data corruption.

<div id="id74" class="section">

#### Values accepted[¶](#id74 "Permalink to this headline")

(since 2.5) Comma-separated list of protocols (not case sensitive) among: `LL`, `LL128`, and `Simple`. To specify protocols to exclude (instead of to include), start the list with `^`.

The default behavior enables all supported algorithms: equivalent to `LL,LL128,Simple` on platforms which support LL128, and `LL,Simple` otherwise.

(since 2.24) The accepted values are expanded to allow more flexibility, just as decribed for `NCCL_ALGO` above, allowing the user to specify protocols for each function.

</div>

</div>

<div id="nccl-nvb-disable" class="section">

### NCCL\_NVB\_DISABLE[¶](#nccl-nvb-disable "Permalink to this headline")

(since 2.11)

Disable intra-node communication through NVLink via an intermediate GPU.

<div id="id75" class="section">

#### Value accepted[¶](#id75 "Permalink to this headline")

Default is 0, set to 1 to disable this mechanism.

</div>

</div>

<div id="nccl-pxn-disable" class="section">

### NCCL\_PXN\_DISABLE[¶](#nccl-pxn-disable "Permalink to this headline")

(since 2.12)

Disable inter-node communication using a non-local NIC, using NVLink and an intermediate GPU.

<div id="id76" class="section">

#### Value accepted[¶](#id76 "Permalink to this headline")

Default is 0, set to 1 to disable this mechanism.

</div>

</div>

<div id="nccl-p2p-pxn-level" class="section">

### NCCL\_P2P\_PXN\_LEVEL[¶](#nccl-p2p-pxn-level "Permalink to this headline")

(since 2.12)

Control in which cases PXN is used for send/receive operations.

<div id="id77" class="section">

#### Value accepted[¶](#id77 "Permalink to this headline")

A value of 0 will disable the use of PXN for send/receive. A value of 1 will enable the use of PXN when the NIC preferred by the destination is not accessible through PCI switches. A value of 2 (default) will cause PXN to always be used, even if the NIC is connected through PCI switches, storing data from all GPUs within the node on an intermediate GPU to maximize aggregation.

</div>

</div>

<div id="nccl-pxn-c2c" class="section">

### NCCL\_PXN\_C2C[¶](#nccl-pxn-c2c "Permalink to this headline")

(since 2.27)

Allow NCCL to use the PXN mechanism if the peer GPU is connected through C2C + PCIe to the targeted NIC.

<div id="id78" class="section">

#### Value accepted[¶](#id78 "Permalink to this headline")

Default is 1 (since NCCL 2.28; it was 0 in NCCL 2.27). Set to 1 to enable and to 0 to disable.

</div>

</div>

<div id="nccl-runtime-connect" class="section">

### NCCL\_RUNTIME\_CONNECT[¶](#nccl-runtime-connect "Permalink to this headline")

(since 2.22)

Dynamically connect peers during runtime (e.g., calling ncclAllreduce()) instead of init stage.

<div id="id79" class="section">

#### Value accepted[¶](#id79 "Permalink to this headline")

Default is 1, set to 0 to connect peers at init stage.

</div>

</div>

<div id="nccl-graph-register" class="section">

<span id="id80"></span>

### NCCL\_GRAPH\_REGISTER[¶](#nccl-graph-register "Permalink to this headline")

(since 2.11)

Enable user buffer registration when NCCL calls are captured by CUDA Graphs.

Effective only when: (i) the CollNet algorithm is being used; (ii) all GPUs within a node have P2P access to each other; (iii) there is at most one GPU per process.

User buffer registration may reduce the number of data copies between user buffers and the internal buffers of NCCL. The user buffers will be automatically de-registered when the CUDA Graphs are destroyed.

<div id="id81" class="section">

#### Value accepted[¶](#id81 "Permalink to this headline")

0 or 1. Default value is 1 (enabled).

</div>

</div>

<div id="nccl-local-register" class="section">

### NCCL\_LOCAL\_REGISTER[¶](#nccl-local-register "Permalink to this headline")

(since 2.19)

Enable user local buffer registration when users explicitly call *ncclCommRegister*.

<div id="id82" class="section">

#### Value accepted[¶](#id82 "Permalink to this headline")

0 or 1. Default value is 1 (enabled).

</div>

</div>

<div id="nccl-legacy-cuda-register" class="section">

### NCCL\_LEGACY\_CUDA\_REGISTER[¶](#nccl-legacy-cuda-register "Permalink to this headline")

(since 2.24)

Cuda buffers allocated through *cudaMalloc* (and related memory allocators) are legacy buffers. Registering legacy buffer can cause implicit synchronization, which is unsafe and can possibly cause a hang for NCCL. NCCL disables legacy buffer registration by default, and users should move to cuMem-based memory allocators for buffer registration.

<div id="id83" class="section">

#### Value accepted[¶](#id83 "Permalink to this headline")

0 or 1. Default value is 0 (disabled).

</div>

</div>

<div id="nccl-win-enable" class="section">

### NCCL\_WIN\_ENABLE[¶](#nccl-win-enable "Permalink to this headline")

(since 2.27)

Enable window memory registration.

<div id="id84" class="section">

#### Value accepted[¶](#id84 "Permalink to this headline")

0 or 1. Default value is 1 (enabled).

</div>

</div>

<div id="nccl-set-stack-size" class="section">

### NCCL\_SET\_STACK\_SIZE[¶](#nccl-set-stack-size "Permalink to this headline")

(since 2.9)

Set CUDA kernel stack size to the maximum stack size amongst all NCCL kernels.

It may avoid a CUDA memory reconfiguration on load. Set to 1 if you experience hang due to CUDA memory reconfiguration.

<div id="id85" class="section">

#### Value accepted[¶](#id85 "Permalink to this headline")

0 or 1. Default value is 0 (disabled).

</div>

</div>

<div id="nccl-graph-mixing-support" class="section">

<span id="id86"></span>

### NCCL\_GRAPH\_MIXING\_SUPPORT[¶](#nccl-graph-mixing-support "Permalink to this headline")

(since 2.13)

Enable/disable support for multiple outstanding NCCL calls from parallel CUDA graphs or a CUDA graph and non-captured NCCL calls. NCCL calls are considered outstanding starting from their host-side launch (e.g., a call to ncclAllreduce() for non-captured calls or cudaGraphLaunch() for captured calls) and ending when the device kernel execution completes. With graph mixing support disabled, the following use cases are NOT supported:

1.  Using a NCCL communicator (or split-shared communicators) from parallel graph launches, where parallel means on different streams without dependencies that would serialize their execution.
2.  Launching a non-captured NCCL collective during an outstanding graph launch that uses the same communicator (or split-shared communicators), regardless of stream ordering.

The ability to disable support is motivated by observed hangs in the CUDA launches when support is enabled and multiple ranks have work launched via cudaGraphLaunch from the same thread.

<div id="id87" class="section">

#### Value accepted[¶](#id87 "Permalink to this headline")

0 or 1. Default is 1 (enabled).

</div>

</div>

<div id="nccl-dmabuf-enable" class="section">

### NCCL\_DMABUF\_ENABLE[¶](#nccl-dmabuf-enable "Permalink to this headline")

(since 2.13)

Enable GPU Direct RDMA buffer registration using the Linux dma-buf subsystem.

The Linux dma-buf subsystem allows GPU Direct RDMA capable NICs to read and write CUDA buffers directly without CPU involvement.

<div id="id88" class="section">

#### Value accepted[¶](#id88 "Permalink to this headline")

0 or 1. Default value is 1 (enabled), but the feature is automatically disabled if the Linux kernel or the CUDA/NIC driver do not support it.

</div>

</div>

<div id="nccl-p2p-net-chunksize" class="section">

### NCCL\_P2P\_NET\_CHUNKSIZE[¶](#nccl-p2p-net-chunksize "Permalink to this headline")

(since 2.14)

The `NCCL_P2P_NET_CHUNKSIZE` controls the size of messages sent through the network for ncclSend/ncclRecv operations.

<div id="id89" class="section">

#### Values accepted[¶](#id89 "Permalink to this headline")

The default is 131072 (128 K).

Values are integers, in bytes. The recommendation is to use powers of 2, hence 262144 would be the next value.

</div>

</div>

<div id="nccl-p2p-ll-threshold" class="section">

### NCCL\_P2P\_LL\_THRESHOLD[¶](#nccl-p2p-ll-threshold "Permalink to this headline")

(since 2.14)

The `NCCL_P2P_LL_THRESHOLD` is the maximum message size that NCCL will use the LL protocol for P2P operations.

<div id="id90" class="section">

#### Values accepted[¶](#id90 "Permalink to this headline")

Decimal number. Default is 16384.

</div>

</div>

<div id="nccl-alloc-p2p-net-ll-buffers" class="section">

### NCCL\_ALLOC\_P2P\_NET\_LL\_BUFFERS[¶](#nccl-alloc-p2p-net-ll-buffers "Permalink to this headline")

(since 2.14)

`NCCL_ALLOC_P2P_NET_LL_BUFFERS` instructs communicators to allocate dedicated LL buffers for all P2P network connections. This enables all ranks to use the LL protocol for latency-bound send and receive operations below `NCCL_P2P_LL_THRESHOLD` sizes. Intranode P2P transfers always have dedicated LL buffers allocated. If running all-to-all workloads with high numbers of ranks, this will result in a high scaling memory overhead.

<div id="id91" class="section">

#### Values accepted[¶](#id91 "Permalink to this headline")

0 or 1. Default value is 0 (disabled).

</div>

</div>

<div id="nccl-comm-blocking" class="section">

### NCCL\_COMM\_BLOCKING[¶](#nccl-comm-blocking "Permalink to this headline")

(since 2.14)

The `NCCL_COMM_BLOCKING` variable controls whether NCCL calls are allowed to block or not. This includes all calls to NCCL, including init/finalize functions, as well as communication functions which may also block due to the lazy initialization of connections for send/receive calls. Setting this environment variable will override the `blocking` configuration in all communicators (see [<span class="std std-ref">ncclConfig\_t</span>](api/types.html#ncclconfig)); if not set (undefined), communicator behavior will be determined by the configuration; if not passing configuration, communicators are blocking.

<div id="id92" class="section">

#### Values accepted[¶](#id92 "Permalink to this headline")

0 or 1. 1 indicates blocking communicators, and 0 indicates nonblocking communicators. The default value is undefined.

</div>

</div>

<div id="nccl-cga-cluster-size" class="section">

### NCCL\_CGA\_CLUSTER\_SIZE[¶](#nccl-cga-cluster-size "Permalink to this headline")

(since 2.16)

Set CUDA Cooperative Group Array (CGA) cluster size. On sm90 and later we have an extra level of hierarchy where we can group together several blocks within the Grid, called Thread Block Clusters. Setting this to non-zero will cause NCCL to launch the communication kernels with the Cluster Dimension attribute set accordingly. Setting this environment variable will override the `cgaClusterSize` configuration in all communicators (see [<span class="std std-ref">ncclConfig\_t</span>](api/types.html#ncclconfig)); if not set (undefined), CGA cluster size will be determined by the configuration; if not passing configuration, NCCL will automatically choose the best value.

<div id="id93" class="section">

#### Values accepted[¶](#id93 "Permalink to this headline")

0 to 8. Default value is undefined.

</div>

</div>

<div id="nccl-max-ctas" class="section">

### NCCL\_MAX\_CTAS[¶](#nccl-max-ctas "Permalink to this headline")

(since 2.17)

Set the maximal number of CTAs the NCCL should use. Setting this environment variable will override the `maxCTAs` configuration in all communicators (see [<span class="std std-ref">ncclConfig\_t</span>](api/types.html#ncclconfig)); if not set (undefined), maximal CTAs will be determined by the configuration; if not passing configuration, NCCL will automatically choose the best value.

<div id="id94" class="section">

#### Values accepted[¶](#id94 "Permalink to this headline")

Set to a positive integer value up to 64 (32 prior to 2.25). Default value is undefined.

</div>

</div>

<div id="nccl-min-ctas" class="section">

### NCCL\_MIN\_CTAS[¶](#nccl-min-ctas "Permalink to this headline")

(since 2.17)

Set the minimal number of CTAs the NCCL should use. Setting this environment variable will override the `minCTAs` configuration in all communicators (see [<span class="std std-ref">ncclConfig\_t</span>](api/types.html#ncclconfig)); if not set (undefined), minimal CTAs will be determined by the configuration; if not passing configuration, NCCL will automatically choose the best value.

<div id="id95" class="section">

#### Values accepted[¶](#id95 "Permalink to this headline")

Set to a positive integer value up to 64 (32 prior to 2.25). Default value is undefined.

</div>

</div>

<div id="nccl-nvls-enable" class="section">

<span id="env-nccl-nvls-enable"></span>

### NCCL\_NVLS\_ENABLE[¶](#nccl-nvls-enable "Permalink to this headline")

(since 2.17)

Enable the use of NVLink SHARP (NVLS). NVLink SHARP is available in third-generation NVSwitch systems (NVLink4) with Hopper and later GPU architectures, allowing collectives such as `ncclAllReduce` to be offloaded to the NVSwitch domain. The default value is 2, so NVLS will be disabled automatically on systems which do not support the feature.

<div id="id96" class="section">

#### Values accepted[¶](#id96 "Permalink to this headline")

0: Disable the use of NVLink SHARP. No NVLink SHARP resources will be allocated.

1: Enable NVLink SHARP. NCCL initialization will fail if the NVLink SHARP resources cannot be allocated.

2: Automatic detection of NVLink SHARP support. Will *not* fail if NVLS is unsupported or if NVLink SHARP resources cannot be allocated.

</div>

</div>

<div id="nccl-ib-merge-nics" class="section">

### NCCL\_IB\_MERGE\_NICS[¶](#nccl-ib-merge-nics "Permalink to this headline")

(since 2.20)

Enable NCCL to combine dual-port IB NICs into a single logical network device. This allows NCCL to more easily aggregate dual-port NIC bandwidth.

<div id="id97" class="section">

#### Values accepted[¶](#id97 "Permalink to this headline")

Default is 1 (enabled), define and set to 0 to disable NIC merging

</div>

</div>

<div id="nccl-mnnvl-enable" class="section">

### NCCL\_MNNVL\_ENABLE[¶](#nccl-mnnvl-enable "Permalink to this headline")

(since 2.21)

Enable NCCL to use Multi-Node NVLink (MNNVL) when available. If the system or driver are not Multi-Node NVLink capable then MNNVL will automatically be disabled. This feature also requires NCCL CUMEM support (`NCCL_CUMEM_ENABLE`) to be enabled. MNNVL requires a fully configured and operational IMEX domain for all the nodes that form the NVLink domain. See the CUDA documentation for more details on IMEX domains.

<div id="id98" class="section">

#### Values accepted[¶](#id98 "Permalink to this headline")

0: Disable MNNVL support.

1: Enable MNNVL support. NCCL initialization will fail if MNNVL is not supported or cannot be enabled.

2: Automatic detection of MNNVL support. Will *not* fail if MNNVL is unsupported or if MNNVL resources cannot be allocated.

</div>

</div>

<div id="nccl-mnnvl-uuid" class="section">

### NCCL\_MNNVL\_UUID[¶](#nccl-mnnvl-uuid "Permalink to this headline")

(since 2.25) Can be used to set the Multi-Node NVLink (MNNVL) UUID to a user defined value. The supplied value will be assigned to both the upper and lower 64-bit words of the 128-bit UUID. Normally the MNNVL UUID is assigned by the Fabric Manager, and it should not need to be overridden.

<div id="id99" class="section">

#### Values accepted[¶](#id99 "Permalink to this headline")

64-bit integer value.

</div>

</div>

<div id="nccl-mnnvl-clique-id" class="section">

### NCCL\_MNNVL\_CLIQUE\_ID[¶](#nccl-mnnvl-clique-id "Permalink to this headline")

(since 2.25) Can be used to set the Multi-Node NVLink (MNNVL) Clique Id to a user defined value. Normally the Clique Id is assigned by the Fabric Manager, but this environment variable can be used to “soft” partition MNNVL jobs. i.e. NCCL will only treat ranks with the same \<UUID,CLIQUE\_ID\> as being part of the same NVLink domain.

<div id="id100" class="section">

#### Values accepted[¶](#id100 "Permalink to this headline")

32-bit integer value.

</div>

</div>

<div id="nccl-ras-enable" class="section">

<span id="env-nccl-ras-enable"></span>

### NCCL\_RAS\_ENABLE[¶](#nccl-ras-enable "Permalink to this headline")

(since 2.24)

Enable NCCL’s reliability, availability, and serviceability (RAS) subsystem, which can be used to query the health of NCCL jobs during execution (see [<span class="doc">RAS</span>](troubleshooting/ras.html)).

<div id="id101" class="section">

#### Values accepted[¶](#id101 "Permalink to this headline")

Default is 1 (enabled); define and set to 0 to disable RAS.

</div>

</div>

<div id="nccl-ras-addr" class="section">

<span id="env-nccl-ras-addr"></span>

### NCCL\_RAS\_ADDR[¶](#nccl-ras-addr "Permalink to this headline")

(since 2.24)

Specify the IP address and port number of a socket that the RAS subsystem will listen on for client connections. RAS can share this socket between multiple processes but that would not be desirable if multiple independent NCCL jobs share a single node (and if those jobs belong to different users, the OS will not allow the socket to be shared). In such cases, each job should be started with a different value (e.g., `localhost:12345`, `localhost:12346`, etc.). Since `localhost` is normally used, only those with access to the nodes where the job is running can connect to the socket. If desired, the address of an externally accessible network interface can be specified instead, which will make RAS accessible from other nodes (such as a cluster’s head node), but that has security implications that should be considered.

<div id="id102" class="section">

#### Values accepted[¶](#id102 "Permalink to this headline")

Default is `localhost:28028`. Either a host name or an IP address can be used for the first part; an IPv6 address needs to be enclosed in square brackets (e.g., `[::1]`).

</div>

</div>

<div id="nccl-ras-timeout-factor" class="section">

### NCCL\_RAS\_TIMEOUT\_FACTOR[¶](#nccl-ras-timeout-factor "Permalink to this headline")

(since 2.24)

Specify the multiplier factor to apply to all the timeouts of the RAS subsystem. RAS relies on multiple timeouts, ranging from 5 to 60 seconds, to determine the state of the application and to maintain its internal communication, with complex interdependecies between different timeouts. This variable can be used to scale up all these timeouts in a safe, consistent manner, should any of the defaults turn out to be too small; e.g., if the NCCL application is subject to high-overhead debugging/tracing/etc., which makes its execution less predictable. If one wants to use the `ncclras` client in such circumstances, its timeout may need to be increased as well (or disabled).

<div id="id103" class="section">

#### Values accepted[¶](#id103 "Permalink to this headline")

Default is 1; define and set to larger values to increase the timeouts.

</div>

</div>

<div id="nccl-launch-order-implicit" class="section">

<span id="id104"></span>

### NCCL\_LAUNCH\_ORDER\_IMPLICIT[¶](#nccl-launch-order-implicit "Permalink to this headline")

(since 2.26)

Implicitly order NCCL operations from different communicators on the same device using the host program order. This ensures the operations will not deadlock. When the CUDA runtime and driver are 12.3+, overlapped execution is permitted. On older CUDA versions the operations will be serialized.

<div id="id105" class="section">

#### Values accepted[¶](#id105 "Permalink to this headline")

Default is 0 (disabled); set to 1 to enable.

</div>

</div>

<div id="nccl-launch-race-fatal" class="section">

### NCCL\_LAUNCH\_RACE\_FATAL[¶](#nccl-launch-race-fatal "Permalink to this headline")

(since 2.26)

Attempt to catch host threads racing to launch to the same device and if so return a fatal error. Such a race would violate the determinacy of the program order relied upon by NCCL\_LAUNCH\_ORDER\_IMPLICIT.

<div id="id106" class="section">

#### Values accepted[¶](#id106 "Permalink to this headline")

Default is 1 (enabled); set to 0 to disable.

</div>

</div>

</div>

</div>

</div>

</div>

<div class="rst-footer-buttons" role="navigation" aria-label="footer navigation">

[Next <span class="fa fa-arrow-circle-right"></span>](troubleshooting.html "Troubleshooting") [<span class="fa fa-arrow-circle-left"></span> Previous](mpi.html "NCCL and MPI")

</div>

-----

<div role="contentinfo">

© Copyright 2020, NVIDIA Corporation

</div>

Built with [Sphinx](http://sphinx-doc.org/) using a [theme](https://github.com/rtfd/sphinx_rtd_theme) provided by [Read the Docs](https://readthedocs.org).

</div>

</div>

</div>

</div>
